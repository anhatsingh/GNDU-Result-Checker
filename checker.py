from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import Select
import os, logging
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

def getData(setup, postData, field):
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
    driver = webdriver.Chrome(ChromeDriverManager().install(), options = opt)

    try:
        driver.get(setup['url'])
                
        for i in postData:
            #print(postData[i])
            Select(driver.find_element(By.ID, i)).select_by_value(postData[i])
            time.sleep(2)
        
        vs = driver.find_element(By.ID, field).find_elements(By.XPATH, ".//*")
        vs = [i.get_attribute("value") for i in vs]
        driver.close()
        return vs 
    except Exception as e:
        logger.exception('Error occurred while retrieving data from GNDU Result Page')
        return []




# get data from the gndu page
def fetchCycle(setup):
    postData = { #post data
     'DrpDwnYear': str(setup['year']),
     'DrpDwnMonth': str(setup['month']),
     'DropDownCourseType': 'C'
    }
    postData2 = postData.copy()
    try:
        data = getData(setup, postData, "DrpDwnCMaster")
        L = [int(i) for i in data if i in list(map(str, setup['department']))]
        final_courses = []
        if len(L) > 0:
            print(L)
            for x in L:
                postData2["DrpDwnCMaster"] = str(x)
                sem_data = getData(setup, postData2, "DrpDwnCdetail")
                print(sem_data)
                sem_found = True if (str(x) + "0" + str(setup['semester'])) in sem_data else False
                if sem_found:
                    final_courses.append(x)
        return list(set(final_courses))
    except:
        logger.exception('Error occurred during fetch cycle')
        return []




def run(sleeptime, setup, paths):
        found = []
        while(len(found) < len(setup['department'])):
            logger.info("Checking for Result")
            try:
                found = fetchCycle(setup)
                with open(paths['checker_data'], 'w') as file:
                    string = f'''Last check at: {time.strftime('%I:%M:%S %p on %b %d, %Y')}\n{'Found: ' + str(found) if len(found) > 0 else 'Alas, nothing was found!'}'''
                    file.write(string)
                logger.info(f'Sleeping for {sleeptime/60} minutes')
                time.sleep(sleeptime)
            except:
                logger.exception('Error occurred while running checker cycle')

        logger.info("Exiting Checker")







if __name__=='__main__':
    logging.basicConfig(filename='debug.log', level=logging.INFO, format='[%(levelname)s %(asctime)s %(name)s %(process)d %(threadName)s] ' + '%(message)s')

    paths = {
        'checker_data': 'dummy_checker.txt'
    }
    dummy_setup = {
        'url' : 'https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULT.aspx',
        'department': [1703, 1702],
        'year': 2021,
        'month': 5,
    }
    run(10, dummy_setup, paths)