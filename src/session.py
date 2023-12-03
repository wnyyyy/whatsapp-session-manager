from asyncio import Lock
import time
import util
from selenium import webdriver

class Session:
    def __init__(self, name: str, service):
        self.name = name
        self.driver = None
        self.running = False
        self.logged_in = False
        self.service = service
        
    def run(self):
        if self.running:
            return
        session_path = util.get_session_path(self.name)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'--user-data-dir={session_path}')
               
        driver = webdriver.Chrome(service=self.service, options=chrome_options)
        driver.get('https://web.whatsapp.com')
        
        self.driver = driver
        self.running = True
        time.sleep(9999)
    
    def quit(self):
        self.driver.quit()
        self.running = False
        self.logged_in = False
