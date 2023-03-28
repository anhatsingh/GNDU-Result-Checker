import pandas as pd
import threading
import queue
import time, requests, traceback
from sheets_api_v5 import googleAPI
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def uploadToGoogle(data, sheet_title, workbook_id):
    try:        
        api = googleAPI(workbook_id, sheet_title)
        api.connectToGoogle()
        gid = api.add_sheet(sheet_title)
        api.setGid(gid)
        api.updateSheet(f"'{sheet_title}'!A1:" + api.getLetter(len(data[0]) - 1) + str(len(data)), data)
        api.sort_sheet(2, True)
        return ("https://docs.google.com/spreadsheets/d/{}/edit#gid={}".format(workbook_id, gid))        
    except:
        return False

not_found_list = []
def get_each_student_data(rollNumber, postData, Q):
    try:
        data = {
                'textboxRno': int(rollNumber),
                'buttonShowResult': 'Submit',

                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATE': postData[0],
                '__VIEWSTATEGENERATOR': '72A7EE3D',
        }
        newData = postData[1] | data
        session = requests.session()
        session.post("https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULT.aspx", data=newData)
        text = session.get("https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULTDISPLAY.aspx").text
        
        soup = BeautifulSoup(text, features="html.parser")
        b = soup.select('#form1')[0]
        table2 = b.find_all("table")[1]
        table3 = b.find_all("table")[2]

        tab2_tr = table2.find_all("tr")
        tab3_tr = table3.find_all("tr")
        data = {
            "Roll Number":          soup.select('#form1 > center > table > span:nth-child(3) > b > tr:nth-child(1) > td:nth-child(1) > b:nth-child(1)')[0].getText(),
            #"Registration Number":  soup.select('#form1 > center > table > span:nth-child(3) > b > tr:nth-child(1) > td:nth-child(2) > b:nth-child(1)')[0].getText(),
            "Name":                 soup.select('#form1 > center > table > span:nth-child(3) > b > tr:nth-child(2) > td:nth-child(1) > b:nth-child(2)')[0].getText(),
            #"Supply":               soup.select('#form1 > center > table > span:nth-child(3) > b > tr:nth-child(2) > td:nth-child(2) > b:nth-child(1)')[0].getText(),
            "CGPA":                 tab3_tr[3].find_all("td")[1].find_all("b")[0].text,
            "SGPA":                 tab3_tr[2].find_all("td")[1].find_all("b")[0].text
            }
        
        for i in range(len(tab2_tr) - 1):
            data[tab2_tr[i+1].find_all("td")[0].getText().strip()] = tab2_tr[i+1].find_all("td")[6].getText().strip()
        

        Q.put(data)
    
    except Exception as e:
        not_found_list.append(rollNumber)
        #printc(f'Data not Found : {rollNumber}')
        #print(traceback.print_exc())
        #Q.put(None)
    
def view_state_finder(postData):
    # set options for chromedriver of selenium
    try:
        opt = Options()
        opt.add_argument("--disable-infobars")
        opt.add_argument("start-maximized")
        opt.add_argument("--disable-extensions")
        opt.add_argument("--headless")        
        # Pass the argument 1 to allow and 2 to block
        
        opt.add_experimental_option("prefs", { \
            "profile.default_content_setting_values.media_stream_mic": 1, 
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.geolocation": 0, 
            "profile.default_content_setting_values.notifications": 1,            
        })
        opt.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opt)
        driver.get("https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULT.aspx")
        WebDriverWait(driver, 300).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#DrpDwnYear')))
        
        for i in postData:        
            Select(driver.find_element(By.ID, i)).select_by_value(postData[i])
            time.sleep(2)
        
        vs = driver.find_element(By.ID, "__VIEWSTATE").get_attribute("value")
        driver.close()        
        return vs
    except:
        print('Error while getting view state in fetcher')
        print("============================================================================")
        print(traceback.format_exc())
        print("============================================================================")
        return None

def printc(text, **kwargs):
    print("[Fetcher] {}".format(text), **kwargs)


def fetch_data(year_month_sem, roll_file):
    print("Initiating Fetcher\nYear : {}\nMonth : {}\nSemester : {}".format(year_month_sem["year"], year_month_sem["month"], year_month_sem["semester"]))    
    df = pd.read_csv(roll_file)    
    course_codes = list(map(int, list(set(df["roll_no"] // 1e7))))    
    view_state_list = dict()


    for i in course_codes:
        printc(f"Fetching ViewState for Course {i}")
        postData = { #post data
                'DrpDwnYear': str(year_month_sem["year"]),
                'DrpDwnMonth': str(year_month_sem["month"]),
                'DropDownCourseType': 'C',
                'DrpDwnCMaster': str(i), #change course here
                'DrpDwnCdetail': str(i) + '0' + str(year_month_sem["semester"]),    #change semester here
            }
        vs = view_state_finder(postData)
        if vs != None:
            view_state_list[i] = (vs, postData)
        print("{}...".format(vs[0:40] if vs != None else vs))

    printc("Fetching Results")
    Q = queue.Queue()
    processes = {}

    printc("Starting Processes")
    for roll in df['roll_no']:
        course_code = int(roll//1e7)
        if course_code in view_state_list:            
            processes[roll] = threading.Thread(target=get_each_student_data, args=(roll, view_state_list[course_code], Q))

    for roll, thread in processes.items():
        try:            
            thread.daemon = True
            thread.start()
        except:
            printc('Error while initiating process')
            print("============================================================================")
            print(traceback.format_exc())
            print("============================================================================")

    
    done = 0
    for roll, thread in processes.items():
        thread.join()
        done+=1
        rolls = list(processes.keys())
        if roll != rolls[-1]:
            printc("Total Done = {}/{}".format(done, len(rolls)), end="\r")
        else:
            printc("Total Done = {}/{}".format(done, len(rolls)), end="\n")
    
    data = []
    while not Q.empty():
        data.append(Q.get())
    
    df2= pd.DataFrame.from_dict(data)    
    df2 = df2.fillna('')
    return df2
    


def run_fetcher(batch_start_year, file_containing_roll, google_workbook_link, sem):
    workbook_id = google_workbook_link   
    months = [5,12]    
    setup = {
        "year": batch_start_year + sem//2,
        "month": months[sem%2],
        "semester": sem
    }

    data = fetch_data(setup, file_containing_roll)

    values = [data.columns.values.tolist()]
    values.extend(data.values.tolist())
    google_link = uploadToGoogle(values, "Semester_{}".format(setup["semester"]), workbook_id)
    if not google_link:
        printc("Google upload failed, saving locally")
        data.to_csv("Semester_{}".format(setup["semester"]) + '.csv')
    else:
        return google_link, not_found_list

if __name__ == '__main__':
    batch_start_year = 2022
    file_containing_roll = "roll_list2.csv"
    google_workbook_link = "189G8J733COODASX8pPv0SnY4gO1ULIPZWMYIiqhUJb0"
    #workbook_id = "1elPbLoNqYqqttAJYbuH0jqzE91I0zs-WfjDVOwb_nR0" # do not change    

    google_link, nf_list = run_fetcher(batch_start_year, file_containing_roll, google_workbook_link, sem=1)

    print(google_link)

    if len(nf_list) > 0:
        printc("Following roll data not found")
        print(nf_list)    