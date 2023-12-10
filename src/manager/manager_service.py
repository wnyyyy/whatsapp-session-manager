import os
from threading import Thread
import common.util as util
import common.consts as consts
import json
from common.enum import Error
from manager.session import Session

class Options:
    def __init__(self, sessions: list[Session], contact: str):
        self.sessions = sessions
        self.contact = contact

class ManagerService:
    def __init__(self):
        self.sessions = []
        self._load_sessions()
        
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
        num_groups = 1
        
        for session in sessions:
            session.run(headless=False)
            session.login()
        for session in sessions:
            has_logged_in = session.get_next_response()
            if isinstance(has_logged_in.type, Error):
                self._handle_session_error(session, has_logged_in)
            else:
                self.log(session, "💫 Logado com sucesso !! 💫")
                
        for session in sessions:
            session.contact_check(contact)
        for session in sessions:
            has_contact = session.get_next_response()
            if isinstance(has_contact.type, Error):
                self._handle_session_error(session, has_contact)
            else:
                self.log(session, "😈 Contato encontrado !! 😈")
        
        while num_groups > 0:
            for session in sessions:
                self._create_group(session, contact)
            num_groups -= 1
                
    def _create_group(self, session: Session, contact: str, file_path: str, group_name: str):
        session.begin_group_creation()
        session.add_group_member(contact)
        session.setup_group(file_path, group_name)
        
    def _handle_session_error(self, session: Session, err: Error):
        self.log(session, f'🤔 ERRO - {err.type.value} 🤔 {f' -> {err.args['data']}' if 'data' in err.args.keys() else ''}')
        session.quit()
        
    def _load_sessions(self):
        config_path = consts.WORK_DIR + '/config.json'
        sessions = []
        if not os.path.exists(config_path):
            with open(config_path, 'w') as file:
                json.dump([], file)
        else:
            with open(config_path, 'r') as file:
                sessions = json.load(file)
        for session in sessions:
            s = Session(session['name'], session['number'])
            self.sessions.append(s)
        self._create_csv()
            
    def _create_csv(self):
        csv_path = consts.WORK_DIR + '/contacts.csv'
        csv_str = consts.CSV_HEADER
        for session in self.sessions:
            csv_str += (f'Bot {util.format_name(session.name)},Bot {util.format_name(session.name)},,,,,,,,,,,,,,,,,,,,,,,,,,,* myContacts,Mobile,{util.format_number(session.number)}\n')
        with open(csv_path, 'w') as file:
            file.write(csv_str)