import numpy as np
import pandas as pd
import threading
import queue
import sys, traceback
import time, requests
import logging
if __name__ == '__main__':
    from sheets_api_v5 import googleAPI
else:
    from fetcher.sheets_api_v5 import googleAPI
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class Fetcher:
    def __init__(self, setup, paths, sleepTime):
        self.config = setup
        self.locations = paths
        self.sleepTime = sleepTime
        self.number_of_retries = 0

    def view_state_finder(self, formUrl, postData):
        # set options for chromedriver of selenium
        opt = Options()
        opt.add_argument("--disable-infobars")
        opt.add_argument("start-maximized")
        opt.add_argument("--disable-extensions")
        opt.headless = True
        # Pass the argument 1 to allow and 2 to block
        
        opt.add_experimental_option("prefs", { \
            "profile.default_content_setting_values.media_stream_mic": 1, 
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.geolocation": 0, 
            "profile.default_content_setting_values.notifications": 1,            
        })
        opt.add_experimental_option('excludeSwitches', ['enable-logging'])

        try:
            driver = webdriver.Chrome(ChromeDriverManager(log_level=0).install(), options = opt)
            driver.get(formUrl)
            WebDriverWait(driver, 300).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#DrpDwnYear')))
            
            for i in postData:
                #print(postData[i])
                Select(driver.find_element(By.ID, i)).select_by_value(postData[i])
                time.sleep(2)
            
            vs = driver.find_element(By.ID, "__VIEWSTATE").get_attribute("value")
            driver.close()
            self.number_of_retries = 0
            return vs
        except:
            if self.number_of_retries < 30:
                time.sleep(10)
                self.number_of_retries += 1
                return self.view_state_finder(formUrl, postData)
            logger.exception(f'Retry {self.number_of_retries}: Error while getting view state in fetcher')


    def get_each_student_data(self, rollNumber, viewState, postData, getUrl, displayUrl, subjects, Q):
        try:
            data = {
                    'textboxRno': int(rollNumber),
                    'buttonShowResult': 'Submit',

                    '__EVENTTARGET': '',
                    '__EVENTARGUMENT': '',
                    '__LASTFOCUS': '',
                    '__VIEWSTATE': viewState,
                    '__VIEWSTATEGENERATOR': '72A7EE3D',
            }
            newData = postData | data
            session = requests.session()
            session.post(getUrl, data=newData)
            text = session.get(displayUrl).text
            
            soup = BeautifulSoup(text, features="html.parser")
            b = soup.select('#form1')[0]
            table2 = b.find_all("table")[1]
            table3 = b.find_all("table")[2]

            tab2_tr = table2.find_all("tr")
            tab3_tr = table3.find_all("tr")
            data = {
                "Roll Number":          soup.select('#form1 > center > table > span:nth-child(3) > b > tr:nth-child(1) > td:nth-child(1) > b:nth-child(1)')[0].getText(),
                "Registration Number":  soup.select('#form1 > center > table > span:nth-child(3) > b > tr:nth-child(1) > td:nth-child(2) > b:nth-child(1)')[0].getText(),
                "Name":                 soup.select('#form1 > center > table > span:nth-child(3) > b > tr:nth-child(2) > td:nth-child(1) > b:nth-child(2)')[0].getText(),
                "Supply":               soup.select('#form1 > center > table > span:nth-child(3) > b > tr:nth-child(2) > td:nth-child(2) > b:nth-child(1)')[0].getText(),
                "CGPA":                 tab3_tr[3].find_all("td")[1].find_all("b")[0].text,
                "SGPA":                 tab3_tr[2].find_all("td")[1].find_all("b")[0].text
                }
            
            for i in range(subjects):
                data[tab2_tr[i+1].find_all("td")[0].getText().strip()] = tab2_tr[i+1].find_all("td")[6].getText().strip()

            Q.put(data)
        
        except Exception as e:
            logger.warning(f'Not Found {rollNumber}')
            #print(traceback.print_exc())
            #Q.put(None)

    def uploadToGoogle(self, sData, sheetTitle, txt_file_location, is_first_run):
        try:            
            sheetID = ''
            with open(txt_file_location) as file:
                sheetID = file.readline().strip('\n')
            
            api = googleAPI(sheetID, sheetTitle)
            api.connectToGoogle()
            
            if is_first_run:
                api.setGid(api.add_sheet(sheetTitle))
                s1 = api.get_gid("Sheet1")
                if s1 is not None:
                    api.delete_sheet(s1)            
            else:
                sheet_gid = api.get_gid(sheetTitle)
                if sheet_gid is not None:
                    api.setGid(sheet_gid)
                else:
                    api.setGid(api.add_sheet(sheetTitle))

            api.updateSheet(f"'{sheetTitle}'!A1:" + api.getLetter(len(sData[0]) - 1) + str(len(sData)), sData)
            api.sort_sheet(4, True)
            return True
        except:
            return False

    def run(self):
        setup = self.config
        paths = self.locations
        logger.info('Fetching Result')
        students = setup['iniRoll'] + np.arange(setup['totalStu'])
        students = np.append(students, setup['rollNumberToCrawl'])
        postData = { #post data
            'DrpDwnYear': str(setup['Year']),
            'DrpDwnMonth': str(setup['Month']),
            'DropDownCourseType': 'C',
            'DrpDwnCMaster': str(setup['CourseCode']), #change course here
            'DrpDwnCdetail': str(setup['CourseCode']) + '0' + str(setup['Semester']),    #change semester here
        }
        viewState = self.view_state_finder(setup['ResultPage'], postData)

        found = 0
        first_run = True
        while(found < setup['totalStu'] - 10):
            Q = queue.Queue()
            processes = []

            for number in students:
                processes.append(threading.Thread(target=self.get_each_student_data, args=(number, viewState, postData, setup['ResultPage'], setup['DisplayPage'], setup['numberofsubjects'], Q)))

            for i in processes:
                i.daemon = True
                i.start()
            
            for i in processes:
                i.join()
            
            data = []

            while not Q.empty():
                data.append(Q.get())
            
            if len(data) > found:
                df = pd.DataFrame.from_dict(data)
                
                df = df.fillna('')
                values = [df.columns.values.tolist()]
                values.extend(df.values.tolist())
                
                self.uploadToGoogle(values, setup['sheetTitle'], paths['sheets_data'], first_run)
                #if not self.uploadToGoogle(values, setup['sheetTitle'], paths['sheets_data']):
                    #print("Upload Failed, Saving Locally")
                    #df.to_csv(setup['sheetTitle'] + '.csv')
            
            found = len(data)
            first_run = False

            if found < setup['totalStu'] - 10:      # Tolerance if max 10 students not found
                time.sleep(self.sleepTime)
    
    










if __name__ == '__main__':
    logging.basicConfig(filename='debug.log', level=logging.INFO, format='[%(levelname)s %(asctime)s %(name)s %(process)d %(threadName)s] ' + '%(message)s')
    
    api = googleAPI("")
    api.connectToGoogle()
    sheetID = ''
    #api.setSheet(sheetID)
    sheetID = api.createSpreadsheet("Alt Section A and B")
    
    dummy_setup = {
            'rollNumberToCrawl': [17032001507,17032001510,17032007422,17032007456,17032007452,17032007444,17032007430],
            'Year': 2021,
            'Month': 5,
            'CourseCode': 1703,
            'Semester': 2,
            'iniRoll': 17032000301,
            'totalStu': 230,
            'numberofsubjects': 5,
            'sheetTitle': 'Alt Section A and B',
            'ResultPage' : 'https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULT.aspx',
            'DisplayPage': 'https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULTDISPLAY.aspx',
          
        }
        
    paths = {
            'sheets_data': 'dummy_sheet.txt',
            'fetcher_data': 'dummy_fetcher.txt'
    }

    with open(paths['sheets_data'], 'w') as file:
        file.write(sheetID)

    f = Fetcher(dummy_setup, paths)
    f.run()