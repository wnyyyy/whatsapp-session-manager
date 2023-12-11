import os
import random
from threading import Thread
import time
import common.util as util
import common.consts as consts
import json
from common.enum import CommandType, EmojiGroup, Error
from manager.session import Session

class GroupName:
    def __init__(self, display: str, names: list[str], random_chars: list[str]):
        self.display = display
        self.names = names
        self.random_chars = random_chars

class Options:
    def __init__(self, sessions: list[Session], contact: str, group_id: str, num_groups: int):
        self.sessions = sessions
        self.contact = contact
        self.group_id = group_id
        self.num_groups = num_groups

class ManagerService:
    def __init__(self):
        self.sessions = []
        self._load_sessions()
        self._load_names_json()
        
    def create_session(self, session_name, session_number):
        session_path = util.get_session_path(session_name)
        if os.path.exists(session_path):
            return [x for x in self.sessions if x.name == session_name][0]
        os.mkdir(session_path)
        config_path = consts.WORK_DIR + '/config.json'
        with open(config_path, 'r') as file:
            sessions = json.load(file)
        sessions.append({"name": session_name, "number": session_number})
        with open(config_path, 'w') as file:
            json.dump(sessions, file, indent=2)
        session = Session(session_name, session_number)
        self.sessions.append(session)
        self._create_csv()
        return session
    
    def run_script(self, options: Options):
        script_thread = Thread(target=self._run_script, args=(options,))
        script_thread.start()
        
    def log(self, session: Session | None, msg):
        if session is None:
            print(msg)
        else:
            print(f'Sessão "{session.name}": {msg}')
                
    def _run_script(self, options: Options):
        sessions = options.sessions
        contact = options.contact
        group_id = options.group_id
        num_groups = options.num_groups
        group = [x for x in self.names if x.display == group_id][0]
        icons = self._get_group_icons(group)
        curr_icon = 0
        
        for session in sessions:
            session.run(headless=False)
            session.login()
        for session in sessions:
            has_logged_in = session.get_next_response()
            if isinstance(has_logged_in.type, Error):
                self._handle_session_error(session, has_logged_in)
            else:
                emoji = self._get_emoji(EmojiGroup.SUCCESS)
                self.log(session, f'{emoji} Logado com sucesso !! {emoji}')
                
        for session in sessions:
            session.contact_check(contact)
        for session in sessions:
            has_contact = session.get_next_response()
            if isinstance(has_contact.type, Error):
                self._handle_session_error(session, has_contact)
            else:
                emoji = self._get_emoji(EmojiGroup.PROGRESS)
                self.log(session, f'{emoji} Contato encontrado !! {emoji}')
        
        for i in range(num_groups):
            for session in sessions:
                icon = None
                if len(icons) > 0:
                    icon = icons[curr_icon % len(icons)]
                    curr_icon += 1
                self._create_group(session, contact, icon, self._generate_group_name(group))
                if i == 0:
                    time.sleep(consts.SESSION_CREATE_GROUP_DESYNC)
                    
    def _group_creation_listener(self, session: Session):
        counter = 0
        while True:
            begin_creation = session.get_next_response()
            if isinstance(begin_creation.type, Error):
                self._handle_session_error(session, begin_creation)
                break
            add_group_member = session.get_next_response()
            if isinstance(add_group_member.type, Error):
                self._handle_session_error(session, add_group_member)
                break
            setup_group = session.get_next_response()
            if isinstance(setup_group.type, Error):
                self._handle_session_error(session, setup_group)
                break
            elif isinstance(setup_group.command, CommandType.SETUP_GROUP):
                counter += 1
                emoji = self._get_emoji(EmojiGroup.PROGRESS)
                self.log(session, f'{emoji} Grupo {counter} criado com sucesso !! {emoji}')
                break
            else:
                emoji = self._get_emoji(EmojiGroup.FAILURE)
                self.log(session, f'{emoji} Algo errado?? {emoji}')
                    
    def _generate_group_name(self, group_name: GroupName):
        curr_name = random.choice(group_name.names) if len(group_name.names) > 0 else ''
        prev_rnd = ''
        while '{r}' in curr_name:
            curr_rnd = random.choice(group_name.random_chars)
            if len(group_name.random_chars) > 1:                
                while curr_rnd == prev_rnd:
                    curr_rnd = random.choice(group_name.random_chars)
            curr_name = curr_name.replace('{r}', curr_rnd, 1)
            prev_rnd = curr_rnd
        return curr_name
    
    def _get_group_icons(self, group_name: GroupName):
        icons_folder = consts.WORK_DIR + '/icons/' + group_name.display
        icons = [f for f in os.listdir(icons_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'))]
        icons_path = [os.path.join(icons_folder, f) for f in icons]
        return icons_path
                
    def _create_group(self, session: Session, contact: str, icon_path: str, group_name: str):
        session.begin_group_creation()
        session.add_group_member(contact)
        session.setup_group(icon_path, group_name)
        
    def _handle_session_error(self, session: Session, err: Error):
        emoji = self._get_emoji(EmojiGroup.FAILURE)
        self.log(session, f'{emoji} ERRO - {err.type.value} {emoji} {f' -> {err.args['data']}' if 'data' in err.args.keys() else ''}')
        session.quit()
        
    def _load_sessions(self):
        config_path = consts.WORK_DIR + '/config.json'
        sessions = []
        if not os.path.exists(config_path):
            with open(config_path, 'w', encoding="utf-8") as file:
                json.dump([], file)
        else:
            with open(config_path, 'r', encoding="utf-8") as file:
                sessions = json.load(file)
        for session in sessions:
            s = Session(session['name'], session['number'])
            self.sessions.append(s)
        self._create_csv()
            
    def _create_csv(self):
        csv_path = consts.WORK_DIR + '/contacts.csv'
        csv_str = consts.CSV_HEADER
        for session in self.sessions:
            csv_str += (
                f'Bot {util.format_name(session.name)},Bot {util.format_name(session.name)},,,,,,,,,,,,,,,,,,,,,,,,,,,* myContacts,Mobile,{util.format_number(session.number)}\n')
        with open(csv_path, 'w') as file:
            file.write(csv_str)
            
    def _load_names_json(self):
        names_path = consts.WORK_DIR + '/names.json'
        if not os.path.exists(names_path):
            default_names = [
                GroupName('satanas', ['{r}'*15, '{r}'*17, '{r}'*19, '{r}'*21, '{r}'*23, '{r}'*25], 
                          ['𓂀','𓁿','⸸','◬','𖤍','👹','💀','☠️','👿','👁️⃤','𐌰','פ','ש','ל','𐕣','𐕣','𐕣','𐕣',
                           '⁶⁶⁶','𖤐','𓃶','⚚','🜏','𖤐','𖤐','ק','רק','ת','ᚨ','ᛉ','ץ','נ','פ','ש','Ⲋ','𓅓','Ⲁ','ⲁ','𐌌','ﭏ','𐌸','𐍉','צ','ס','ן','𐍆','𐍁','𐌳','𐌶','𐌼']).__dict__]
                        
            with open(names_path, 'w', encoding="utf-8") as file:
                json.dump(default_names, file, indent=2, ensure_ascii=False)        
        with open(names_path, 'r', encoding="utf-8") as file:
            self.names = json.load(file)
            names_obj = []
            for name in self.names:
                name = GroupName(**name)
                names_obj.append(name)
            self.names = names_obj
            
    def _get_emoji(self, emoji: EmojiGroup):
        return emoji.value[random.randint(0, len(EmojiGroup.SUCCESS.value)-1)]