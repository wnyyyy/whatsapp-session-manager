import os
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
        sessions = options.sessions
        contact = options.contact
        
        for session in sessions:
            session.run()
            session.login()
        for session in sessions:
            session.contact_check(contact)
        for session in sessions:
            has_contact = session.get_next_response()
            if isinstance(has_contact, Error):
                self._handle_session_error(session, has_contact)      
        
    def _handle_session_error(self, session: Session, err: Error):
        print(f'Session "{session.name}": ERRO - {err.value}')
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