from threading import Lock, Thread
import common.consts as consts
import common.util as util
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class Session:
    def __init__(self, name: str, service: Service):
        self.name = name
        self.running = False
        self.logged_in = None
        self.thread = None
        self.service = service
        self.lock = Lock()
        
    def quit(self):
        try:
            self.lock.acquire()
            if self.running:
                if self.thread is not None:
                    try:
                        self.thread.join()
                    except:
                        pass
                self.thread = None
                self.running = False
                self.logged_in = None
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
        try:
            session_path = util.get_session_path(self.name)
            chrome_options = ChromeOptions()
            chrome_options.add_argument(f'--user-data-dir={session_path}')
                
            driver = Chrome(service=self.service, options=chrome_options)
            driver.get('https://web.whatsapp.com')
            
            try:
                self.lock.acquire()
                self.running = True
                self.driver = driver
            finally:
                self.lock.release()
            
            self._try_login()
        except:
            self.quit()
        
    def _try_login(self):
        try:
            WebDriverWait(self.driver, consts.PAGE_LOAD_TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.landing-title'))
            )
            self.logged_in = False
        except TimeoutException:
            try:
                WebDriverWait(self.driver, consts.PAGE_LOAD_TIMEOUT_SECONDS).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="profile photo"]'))
                )
                self.logged_in = True
            except TimeoutException:
                self.logged_in = None
