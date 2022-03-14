import threading, time, logging, os, requests, json, random
import traceback
import checker.app as checker
from fetcher.app import Fetcher
import reporter
from whatsappManager.whatsapp import Whatsapp
from fetcher.sheets_api_v5 import googleAPI
from drive_api_v1 import driveAPI
from config import setup, greeting_msg

# ================================================================================================================================================================
open(setup['paths']['fetcher_data'], 'w').close()
open(setup['paths']['checker_data'], 'w').close()


with open(setup['paths']['reporter_data'], 'w') as file:
    file.write(str(setup['reporter']['run']))

logging.basicConfig(filename='debug.log', level=logging.INFO, format='[%(levelname)s %(asctime)s %(name)s %(process)d %(threadName)s] ' + '%(message)s')
logger = logging.getLogger(__name__)

# ================================================================================================================================================================

if setup['make_new_spreadsheet']:
    open(setup['paths']['sheets_data'], 'w').close()
    api = googleAPI("")
    api.connectToGoogle()
    sheetID = api.createSpreadsheet(setup['spreadsheet_name'])
    drive = driveAPI()
    drive.connect()
    drive.select_file(sheetID)
    drive.share()
else:
    sheets_file = open(setup['paths']['sheets_data'])
    sheetID = sheets_file.readline().strip()
    logger.info(f'Using old Google sheet -> ID: {sheetID}')
    sheets_file.close()

# ================================================================================================================================================================

if setup['make_new_spreadsheet']:
    try:
        logger.info("Generating TinyURL")
        data = {
            "url": f"https://docs.google.com/spreadsheets/d/{sheetID}/edit",
            "domain": "tiny.one",
            "alias": "gndu-" + str(random.randint(1000, 999999))
        }
        response = requests.post(f'https://api.tinyurl.com/create?api_token={setup["tinyurl_api"]}', data=data)
        json_data = json.loads(response.text)
        sheet_url = json_data['data']['tiny_url']
    except:
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheetID}/edit"
else:
    sheets_file = open(setup['paths']['sheets_data'])
    sheets_file.readline()
    sheet_url = sheets_file.readline().strip()
    sheets_file.close()

logger.info(f'Sheet URL: {sheet_url}')

with open(setup['paths']['sheets_data'], 'w') as file:
    file.write(sheetID + '\n' + sheet_url)
# ================================================================================================================================================================

def check_if_fetcher_needs_to_turn_on(whatsapp):
    found_result = []
    fetched_results = []
    fetcher_threads = {}
    while(len(fetched_results) < len(setup['checker']['department'])):
        try:            
            with open(setup['paths']['checker_data']) as file:
                file.readline()
                found_result = file.readline().strip()[8:-1].replace(' ', '').split(',')

            with open(setup['paths']['fetcher_data']) as file:
                fetched_results = list(set(file.read().strip().split('\n')))

            if found_result[0] in list(map(str, setup['checker']['department'])):
                for i in found_result:
                    if i not in fetched_results:                        
                        fetcher_threads[i] = threading.Thread(target=Fetcher(setup['fetcher'][i], setup['paths'], setup['fetcher']['sleep_time_for_partial_result']).run)
                        fetcher_threads[i].start()
                        
                        with open(setup['paths']['fetcher_data'], 'a') as file:
                            file.write(str(setup['fetcher'][i]['CourseCode']) + '\n')
                        whatsapp.cycle_send_all(f'Result Found\n\n{setup["fetcher"][i]["name"]}\nLink: {sheet_url}\n\nIf your roll number is not included, this sheet will update every {setup["fetcher"]["sleep_time_for_partial_result"]/60} minutes')            
        except:
            logging.exception('Error while checking whether to run fetcher')
        
        time.sleep(60)
    
    for i in fetcher_threads:
        fetcher_threads[i].join()
                

if __name__ == "__main__":
    whatsApp = Whatsapp()
    whatsApp.set_chat(setup['whatsapp_chats']['result_found_send_at'])
    whatsApp.set_header(f'BOT v4.3\nTime: {time.strftime("%I:%M:%S %p, %d-%m-%Y")}')

    if setup['greeting']:
        whatsApp.cycle_send_all(greeting_msg)

    # Starting Result Checker
    p1 = threading.Thread(target=checker.run, args=(setup['checker_recheck_time'], setup['checker'], setup['paths']))
    p1.daemon = True
    p1.start()

    # Starting Status Reporter
    p2 = threading.Thread(target=reporter.run, args=(setup,))
    p2.daemon = True
    p2.start()

    p3 = threading.Thread(target=check_if_fetcher_needs_to_turn_on, args = (whatsApp, ))
    p3.daemon = True
    p3.start()

    # Result Found; Kill Checker and Reporter
    p1.join()
    with open(setup['paths']['reporter_data'], 'w') as file:
        file.write(str(False))
    p2.join()
    p3.join()

    whatsApp.cycle_send_all('Everything Done, I am going to sleep, See ya all next sem!\n\nGoodnight!\n\nP.S. If you want to help improve this bot, go to https://github.com/anhatsingh/GNDU-Result-Checker')