import time
import util
from multiprocessing import Process, Queue
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

class Session:
    def __init__(self, name: str):
        self.name = name
        self.running = False
        self.logged_in = False
        self.process = None
        self.command_queue = Queue()
        self.response_queue = Queue()
        
    def quit(self):
        if self.running:
            self.send_command('QUIT')
            if self.process is not None:
                self.process.join()
            self.process = None
            self.running = False
            self.logged_in = False
        
    def send_command(self, command):
        if self.running:
            self.command_queue.put(command)
        
    def run(self):
        if self.running:
            return
        process = Process(target=self._run, args=(self.command_queue, self.response_queue, self.name))
        process.start()
        self.running = True
        self.process = process
        
    def check_responses(self):
        if self.running:
            while not self.response_queue.empty():
                response = self.response_queue.get()
                if response == "LOGGED_IN":
                    self.logged_in = True
        
    @staticmethod
    def _run(command_queue: Queue, response_queue: Queue, name: str):
        session_path = util.get_session_path(name)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'--user-data-dir={session_path}')
               
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get('https://web.whatsapp.com')
        
        while True:
            command = command_queue.get()
            if command == 'QUIT':
                driver.quit()
                break
