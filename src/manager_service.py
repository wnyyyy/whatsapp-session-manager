from asyncio import Lock
import os
import util
import consts
import json
from session import Session
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class ManagerService:
    def __init__(self, lock: Lock):
        self._sessions = []
        self.service = Service(ChromeDriverManager().install())
        self._load_sessions()      
        self._lock = lock  
        
    async def create_session(self, session_name):
        session_path = util.get_session_path(session_name)
        await self._lock.acquire()
        try:
            if os.path.exists(session_path):
                return [x for x in self._sessions if x.name == session_name][0]
            os.mkdir(session_path)
            config_path = consts.WORK_DIR + '/config.json'
            with open(config_path, 'r') as file:
                session_names = json.load(file)
            session_names.append(session_name)
            with open(config_path, 'w') as file:
                json.dump(session_names, file)
            session = Session(session_name, self.service)
            self._sessions.append(session)
        finally:
            self._lock.release()
        return session
    
    async def _load_sessions(self):
        config_path = consts.WORK_DIR + '/config.json'
        await self._lock.acquire()
        try:
            session_names = []
            if not os.path.exists(config_path):
                with open(config_path, 'w') as file:
                    json.dump([], file)
            else:
                with open(config_path, 'r') as file:
                    session_names = json.load(file)
            for session_name in session_names:
                session = Session(session_name, self.service)
                self._sessions.append(session)
        finally:
            self._lock.release()
    
    async def _get_session(self, session_name):
        await self._lock.acquire()
        try:
            for session in self._sessions:
                if session.id == session_name:
                    self._lock.release()
                    return session
        finally:
            self._lock.release()
        return None
        
