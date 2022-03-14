import time, re, traceback, logging, threading
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


chatlist_search = "._13NKt.copyable-text.selectable-text"
first_conversation = "#pane-side > div:nth-child(1) > div > div > div:nth-child(1)"
typing_textbox = "#main > footer > div._2BU3P.tm2tP.copyable-area > div > span:nth-child(2) > div > div._2lMWa > div.p3_M1 > div > div._13NKt.copyable-text.selectable-text"
send_message_button = "._4sWnG"

messages_general = "._22Msk"
each_msg_text = "div._1Gy50 > span > span"
each_msg_time = '._2jGOb.copyable-text'
each_msg_time_format = '[%I:%M %p, %d/%m/%Y]'
each_msg_sender = '.a71At.ajgl1lbb.edeob0r2.i0jNr'

lock = threading.Lock()

class Whatsapp:
    def __init__(self, chats = []):
        self.logger = logging.getLogger(__name__)
        opt = Options()
        opt.add_argument("--disable-infobars")
        opt.add_argument("start-maximized")
        opt.add_argument("--disable-extensions")
        opt.add_argument("user-data-dir=C:\\chromedriver\\user_data\\")
        # Pass the argument 1 to allow and 2 to block
        
        opt.add_experimental_option("prefs", { \
            "profile.default_content_setting_values.media_stream_mic": 1, 
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.geolocation": 0, 
            "profile.default_content_setting_values.notifications": 1,            
        })
        opt.add_experimental_option('excludeSwitches', ['enable-logging'])

        self.options  = opt
        self.chats = chats
        self.header = 'BOTI\n\n'
        self.number_of_retries = 0
    
    def set_chat(self, chats):
        self.chats = chats
    
    def set_header(self, strng):
        self.header = strng + '\n'

    def __compile_with_header(self, msg):
        return self.header + 'Time: {time.strftime("%I:%M:%S %p, %d-%m-%Y")}\n\n' + msg
    
    def open(self):
        try:
            self.driver = webdriver.Chrome(ChromeDriverManager(log_level=0).install(), options = self.options)
            self.driver.get('https://web.whatsapp.com')
            self.driver.implicitly_wait(100)
            WebDriverWait(self.driver, 300).until(EC.visibility_of_element_located((By.CSS_SELECTOR, chatlist_search)))
            self.logger.info('Initiated')
        except:
            self.logger.exception("Error Occurred while opening whatsapp")
    
    def getAllMessages(self, name):
        time.sleep(1)
        self.openConversation(name)        
        parent = self.driver.find_elements(By.CSS_SELECTOR, messages_general)

        self.driver.implicitly_wait(10)
        messages = []
        a = 1        
        for i in parent:        
            try:
                message = i.find_element(By.CSS_SELECTOR, each_msg_text).text
                theTime = i.find_element(By.CSS_SELECTOR, each_msg_time).get_attribute("data-pre-plain-text")
                
                theTime = re.findall(r'\[.*?\]', theTime)
                theTime = datetime.strptime(theTime[0], each_msg_time_format)

                eachMsg = {
                    "id": a,
                    "msg": message,
                    "time": theTime,
                    "sender": i.find_element(By.CSS_SELECTOR, each_msg_sender).text
                }
                messages.append(eachMsg)
                a+=1
            except:            
                self.logger.exception("Error occurred while retrieving messages")
            #do error handling here later.

        return messages
    
    def openConversation(self, name):
        try:
            searchbar = self.driver.find_element(By.CSS_SELECTOR, chatlist_search)
            searchbar.send_keys(name)
            time.sleep(1)
            self.driver.find_element(By.CSS_SELECTOR, first_conversation).click()
            self.logger.info(f'Opened chat: {name}')
            time.sleep(1)
            return True
        except:
            self.logger.exception(f'Error occurred while opening conversation {name}')
            return False
    
    def send_all(self, msg, send_headers = True):
        return_list = []
        if send_headers:
                msg = self.__compile_with_header(msg)

        for i in self.chats:
            return_list.append(self.send_single(i, msg))
        
        return False if False in set(return_list) else True

    def send_single(self, chat_name, msg):
        ''' Sends a whatsapp message to chat_name.
        '''
        try:
            
            time.sleep(1)
            if self.openConversation(chat_name):    
                textarea = self.driver.find_element(By.CSS_SELECTOR, typing_textbox)

                msg = msg.split("\n")        
                for i in msg:
                    textarea.send_keys(i)
                    textarea.send_keys(Keys.SHIFT + Keys.ENTER)

                self.driver.implicitly_wait(100)
                time.sleep(1)        
                self.driver.find_element(By.CSS_SELECTOR, send_message_button).click()
                self.logger.info(f'Message Sent: "{chat_name}" -> {" ".join(msg)}')
                time.sleep(5)
                return True
            else:
                self.logger.exception(f'Unable to send message to "{chat_name}" MSG: {" ".join(msg)}')
                return False
        except:
            self.logger.exception(f'Unable to send message to "{chat_name}" MSG: {" ".join(msg)}')
            return False
    
    def exit(self):
        try:
            self.logger.info('Exiting')
            self.driver.close()
            return True
        except:
            self.logger.exception('Error occurred while exiting whatsapp')
            return False
    
    def cycle_send_all(self, msg):
        try:
            lock.acquire()
            self.open()
            result = self.send_all(msg)
            self.exit()
            lock.release()
            return result
        except:
            if self.number_of_retries < 30:
                time.sleep(10)
                self.number_of_retries += 1
                return self.cycle_send_all(msg)                
            self.logger.exception(f'Retry {self.number_of_retries}: Error occurred while running cycle to send messages')
            return False