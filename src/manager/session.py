from threading import Lock, Thread
import time
import common.consts as consts
import common.util as util
from common.enum import WhatsAppContext
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class Session:
    def __init__(self, name: str, number: str, service: Service):
        self.name = name
        self.number = number
        self.running = False
        self.logged_in = None
        self.context = WhatsAppContext.NONE
        self.thread = None
        self.driver = None
        self.service = service
        self.lock = Lock()
        
    def quit(self):
        try:
            self.lock.acquire()
            if self.running:
                if self.driver is not None:
                    try:
                        self.driver.close()
                    except:
                        pass
                    self.driver = None
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
                
    def begin_group_creation(self):
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
            
    def add_group_member(self, contact):
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
                
    def contact_check(self, contact):
        try:
            self.lock.acquire()
            if self.context != WhatsAppContext.HOME:
                return None
            
            search_box = WebDriverWait(self.driver, consts.DEFAULT_TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[title="Search input textbox"]')))
            search_box.send_keys(contact)

            side_pane = WebDriverWait(self.driver, consts.DEFAULT_TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((By.ID, 'pane-side')))

            WebDriverWait(self.driver, consts.DEFAULT_TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Search results."]')))
            search_results = side_pane.find_element(By.CSS_SELECTOR, '[aria-label="Search results."]')
            if search_results is None:
                return False
            search_results = search_results.find_elements(By.XPATH, "./*")            
            if len(search_results) > 2:
                print("MAIS DE UM CONTATO ENCONTRADO!!!!111!")
                input()
            return True        
        except:
            return None
        finally:
            self.lock.release()
