from collections import namedtuple
from threading import Lock, Thread
import time
import common.consts as consts
import common.util as util
from queue import Queue
from common.enum import CommandType, WhatsAppContext, Error
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

Command = namedtuple('Command', ['type', 'args'])
Response = namedtuple('Response', ['type', 'args'])

class Session:    
    def __init__(self, name: str, number: str):
        self.name = name
        self.number = number
        self._commands = Queue()
        self._responses = Queue()
        self.running = False
        self.logged_in = None
        self.context = WhatsAppContext.NONE
        self.thread = None
        self.driver = None
        self.lock = Lock()
        
    def quit(self):
        self._commands.put(Command(CommandType.QUIT, {}))
        self.thread.join()
        
    def get_next_response(self):
        return self._responses.get()
            
    def contact_check(self, contact: str):
        command = Command(CommandType.CONTACT_CHECK, {'contact': contact})
        self._commands.put(command)
        
    def login(self):
        command = Command(CommandType.LOGIN, {})
        self._commands.put(command)
        
    def run(self, headless: bool = False):
        try:
            self.lock.acquire()
            if self.running:
                return
            self.thread = Thread(target=self._run, args=(headless,))
            self.thread.start()
        finally:
            self.lock.release()
        
    def _run(self, headless: bool = False):
        try:
            session_path = util.get_session_path(self.name)
            chrome_options = ChromeOptions()
            if headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--window-size=1280,720')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
            chrome_options.add_argument(f'--executable-path={consts.WORK_DIR}/chromedriver.exe')
            chrome_options.add_argument(f'--user-data-dir={session_path}')
                
            driver = Chrome(options=chrome_options)
            driver.get('https://web.whatsapp.com')
            
            try:
                self.lock.acquire()
                self.running = True
                self.driver = driver
            finally:
                self.lock.release()
                        
            while True:
                command = self._commands.get()
                if command.type is CommandType.QUIT:
                    self._perform_quit()
                    self._commands.task_done()
                    break
                elif command.type is CommandType.LOGIN:
                    self._try_login()
                elif command.type is CommandType.CONTACT_CHECK:
                    self._contact_check(command.args['contact'])
                self._commands.task_done()
        except:
            self.quit()
            
    def _perform_quit(self):
        if self.driver is not None:
            try:
                self.driver.close()
            except:
                pass
            self.driver = None
        self.thread = None
        self.running = False
        self.logged_in = None
        self.context = WhatsAppContext.NONE
        
    def _try_login(self):
        try:
            WebDriverWait(self.driver, consts.PAGE_LOAD_TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.landing-title'))
            )
            self.logged_in = False
            self.context = WhatsAppContext.LANDING_PAGE
        except TimeoutException:
            try:
                WebDriverWait(self.driver, consts.DEFAULT_TIMEOUT_SECONDS).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="profile photo"]'))
                )
                self.logged_in = True
                self.context = WhatsAppContext.HOME
            except TimeoutException:
                self.logged_in = None
                
    def _begin_group_creation(self):
        try:
            self.lock.acquire()
            if self.context != WhatsAppContext.HOME:
                return None
            time.sleep(consts.UI_INTERACTION_DELAY)
            menu = WebDriverWait(self.driver, consts.DEFAULT_TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-icon="menu"]')))
            menu.click()
                            
            time.sleep(consts.UI_INTERACTION_DELAY)
            new_group_button = WebDriverWait(self.driver, consts.DEFAULT_TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="New group"]')))
            new_group_button.click()
            self.context = WhatsAppContext.GROUP_MEMBERS_SELECT
        except TimeoutException:
            return None
        finally:
            self.lock.release()
            
    def _add_group_member(self, contact):
        try:
            self.lock.acquire()
            if self.context != WhatsAppContext.GROUP_MEMBERS_SELECT:
                return None
            time.sleep(consts.UI_INTERACTION_DELAY)
            search_box = WebDriverWait(self.driver, consts.DEFAULT_TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"].copyable-text.selectable-text')))
            
            time.sleep(consts.UI_INTERACTION_DELAY)
            search_box.send_keys(contact)
            
            time.sleep(consts.UI_INTERACTION_DELAY)
            try:
                results_div = WebDriverWait(self.driver, consts.DEFAULT_TIMEOUT_SECONDS).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-tab="4"]')))
            except:
                return False
            results_div = results_div.find_elements(By.XPATH, "././*")
            if len(results_div) > 1:
                return False
            
            time.sleep(consts.UI_INTERACTION_DELAY)
            results_div[0].click()
            
        except TimeoutException:
            return None
        finally:
            self.lock.release()
                
    def _contact_check(self, contact):
        try:
            self.lock.acquire()
            if self.context != WhatsAppContext.HOME:
                self._responses.put(Response(Error.UNEXPECTED_CONTEXT, {}))
                return
            
            search_box = WebDriverWait(self.driver, consts.DEFAULT_TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[title="Search input textbox"]')))
            search_box.send_keys(contact)

            side_pane = WebDriverWait(self.driver, consts.DEFAULT_TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((By.ID, 'pane-side')))

            WebDriverWait(self.driver, consts.DEFAULT_TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Search results."]')))
            search_results = side_pane.find_element(By.CSS_SELECTOR, '[aria-label="Search results."]')
            if search_results is None:
                self._responses.put(Response(Error.CONTACT_NOT_FOUND, {}))
                return
            search_results = search_results.find_elements(By.XPATH, "./*")            
            if len(search_results) > 2:
                self._responses.put(Response(Error.MORE_THAN_ONE_CONTACT_FOUND, {}))
                return
            self._responses.put(Response({}, {}))
            
            time.sleep(consts.UI_INTERACTION_DELAY)
            
            return_button = WebDriverWait(self.driver, consts.DEFAULT_TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-icon="search"]')))
            return_button.click()
        except:
            return Error.DRIVER_ERROR
        finally:
            self.lock.release()
