import os
import util
import consts
import json
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from session import Session

class ManagerService:
    def __init__(self):
        self.sessions = []
        self.service = Service(ChromeDriverManager().install())
        self._load_sessions()    
        
    def create_session(self, session_name):
        session_path = util.get_session_path(session_name)
        if os.path.exists(session_path):
            return [x for x in self.sessions if x.name == session_name][0]
        os.mkdir(session_path)
        config_path = consts.WORK_DIR + '/config.json'
        with open(config_path, 'r') as file:
            session_names = json.load(file)
        session_names.append(session_name)
        with open(config_path, 'w') as file:
            json.dump(session_names, file)
        session = Session(session_name, self.service)
        self.sessions.append(session)
        return session
    
    def _load_sessions(self):
        config_path = consts.WORK_DIR + '/config.json'
        session_names = []
        if not os.path.exists(config_path):
            with open(config_path, 'w') as file:
                json.dump([], file)
        else:
            with open(config_path, 'r') as file:
                session_names = json.load(file)
        for session_name in session_names:
            session = Session(session_name, self.service)
            self.sessions.append(session)
        
