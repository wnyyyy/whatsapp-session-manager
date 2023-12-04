from threading import Lock, Thread
import time
import util
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

class Session:
    def __init__(self, name: str, service: Service):
        self.name = name
        self.running = False
        self.logged_in = False
        self.thread = None
        self.service = service
        self.lock = Lock()
        
    def quit(self):
        try:
            self.lock.acquire()
            if self.running:
                if self.thread is not None:
                    self.thread.join()
                self.thread = None
                self.running = False
                self.logged_in = False
        finally:
            self.lock.release()
        
    def run(self):
        try:
            self.lock.acquire()
            if self.running:
                return
            self.thread = Thread(target=self._run)
            self.thread.start()
        finally:
            self.lock.release()
        
    def _run(self):
        session_path = util.get_session_path(self.name)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'--user-data-dir={session_path}')
               
        driver = webdriver.Chrome(service=self.service, options=chrome_options)
        driver.get('https://web.whatsapp.com')
        
        try:
            self.lock.acquire()
            self.running = True
        finally:
            self.lock.release()
        
        time.sleep(9999)
