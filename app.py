# all imports required to run the app.
import threading, time, logging, requests, json, random
import checker.app as checker
from fetcher.app import Fetcher
import reporter
from whatsappManager.whatsapp import Whatsapp
from fetcher.sheets_api_v5 import googleAPI
from drive_api_v1 import driveAPI
from config import setup, greeting_msg

# ================================================================================================================================================================

# This will clear/make files required to share data with different modules.
#open(setup['paths']['fetcher_data'], 'w').close()
#open(setup['paths']['checker_data'], 'w').close()

with open(setup['paths']['reporter_data'], 'w') as file:
    # check if we want to run reporter, if yes, write it to file, which will be read later.
    file.write(str(setup['reporter']['run']))

# initiate the logging procedure.
logging.basicConfig(filename='debug.log', level=logging.INFO, format='[%(levelname)s %(asctime)s %(name)s %(process)d %(threadName)s] ' + '%(message)s')
logger = logging.getLogger(__name__)

# ================================================================================================================================================================
# this will create a new Google Workbook, or use an old one.
if setup['make_new_spreadsheet']:
    # clear already saved sheets
    open(setup['paths']['sheets_data'], 'w').close()
    # connect to google api with no old workbook
    api = googleAPI("")
    api.connectToGoogle()
    # create new workbook and assign its id to sheetID
    sheetID = api.createSpreadsheet(setup['spreadsheet_name'])
    # connect to Google drive API
    drive = driveAPI()
    drive.connect()
    # select the file in drive with ID as sheetID
    drive.select_file(sheetID)
    # change the file permissions to share with all having link
    drive.share()
else:
    # use old sheet, whose id is saved in metadata file.
    sheets_file = open(setup['paths']['sheets_data'])
    sheetID = sheets_file.readline().strip()
    logger.info(f'Using old Google sheet -> ID: {sheetID}')
    sheets_file.close()

# ================================================================================================================================================================
# This will try and create a tinyurl, or use an old one.
if setup['make_new_spreadsheet']:
    # if we want to make new workbook, control proceeds into this section
    try:
        logger.info("Generating TinyURL")
        data = {
            "url": f"https://docs.google.com/spreadsheets/d/{sheetID}/edit",
            "domain": "tiny.one",
            "alias": "gndu-" + str(random.randint(1000, 999999))            # the url will be like https://tiny.one/gndu-xxxxxx
        }
        # make the post request to the tinyurl api
        response = requests.post(f'https://api.tinyurl.com/create?api_token={setup["tinyurl_api"]}', data=data)
        # read the response returned from api and parse it as a json object
        json_data = json.loads(response.text)
        # if success, the url will be assigned to sheet_url
        sheet_url = json_data['data']['tiny_url']
    except:
        # if any failure occurs in creating tinyurl, we instead use simple Google Sheets url.
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheetID}/edit"
else:
    # if we do not want to create a new url and use the one saved in metadata, we come here.
    sheets_file = open(setup['paths']['sheets_data'])
    sheets_file.readline()
    sheet_url = sheets_file.readline().strip()
    sheets_file.close()

logger.info(f'Sheet URL: {sheet_url}')

# whereever the sheet id and url came from, save it in a metadata file.
with open(setup['paths']['sheets_data'], 'w') as file:
    file.write(sheetID + '\n' + sheet_url)
# ================================================================================================================================================================

def check_if_fetcher_needs_to_turn_on(whatsapp):
    """This function is called inside a different thread. It checks if we need to run result fetcher or not every 60 seconds.

    Args:
        whatsapp (object): whatsapp class instance to send messages through whatsapp.
    """
    # this stores all the courses whose result is found so far by the result checker.
    found_result = []
    # this stores all the courses whose result is already fetched by the result fetcher. 
    fetched_results = []
    # this stores all the threads that will be initiated to store the result.
    fetcher_threads = {}
    # Run the following block until all the courses' result has been found.
    while(len(fetched_results) < len(setup['checker']['department'])):
        try:
            # read the metadata file that contains the course codes whose results have been found by the checker, and update found_result list
            with open(setup['paths']['checker_data']) as file:
                file.readline()
                found_result = file.readline().strip()[8:-1].replace(' ', '').split(',')

            # read the metadata file that contains the course codes whose results have been fetched by the fetcher, and update fetched_results list
            with open(setup['paths']['fetcher_data']) as file:
                fetched_results = list(set(file.read().strip().split('\n')))

            # check if found result actually contains course codes, and nothing else.
            if found_result[0] in list(map(str, setup['checker']['department'])):
                # check if we have fetched result for every course found by the checker or not.
                for i in found_result:
                    if i not in fetched_results:
                        # if the result is still not fetched, create a thread that will continuously fetch the result until all students' result is fetched.
                        # this thread will not end until atleast total_students - 10 results are found.
                        fetcher_threads[i] = threading.Thread(target=Fetcher(setup['fetcher'][i], setup['paths'], setup['fetcher']['sleep_time_for_partial_result']).run)
                        fetcher_threads[i].daemon = True
                        fetcher_threads[i].start()
                        
                        # write the course code in the list of fetched results by the checker.
                        with open(setup['paths']['fetcher_data'], 'a') as file:
                            file.write(str(setup['fetcher'][i]['CourseCode']) + '\n')
                        
                        # send a whatsapp message indicating we have found the result with the course name and url to the sheet.
                        whatsapp.cycle_send_all(f'Result Found\n\n{setup["fetcher"][i]["name"]}\nLink: {sheet_url}\n\nIf your roll number is not included, this sheet will update every {setup["fetcher"]["sleep_time_for_partial_result"]/60} minutes')            
        except:
            # if any error occurs with the above code, log it.
            logging.exception('Error while checking whether to run fetcher')
        
        # sleep for 1 minute and check again if fetcher needs to run or not.
        time.sleep(60)
    
    # wait for all the fetcher threads to join back after they have fetched all possible results
    for i in fetcher_threads:
        fetcher_threads[i].join()
    # fetcher_check_if_run thread ends here.
                

if __name__ == "__main__":
    # create a Whatsapp class instance
    whatsApp = Whatsapp()
    # set the list of chats we want to send messages to!
    whatsApp.set_chat(setup['whatsapp_chats']['result_found_send_at'])
    # set the common heading of all the messages sent using this class.
    whatsApp.set_header('BOTI v4.5')

    # if we want to send a greeting message before running everything, control executes the following block.
    if setup['greeting']:
        # send a whatsapp message. 
        # Cycle implies: Whatsapp open -> send message -> whatsapp close. And this is a thread-safe operation i.e. it uses semaphores.
        whatsApp.cycle_send_all(greeting_msg)

    # Starting Result Checker
    # make a thread that will check if the result is published or not.
    # set the thread as daemon, so that it exits if main app quits.
    p1 = threading.Thread(target=checker.run, args=(setup['checker_recheck_time'], setup['checker'], setup['paths']))
    p1.daemon = True
    p1.start()

    # Starting Status Reporter
    # make a thread that will report the status on whatsapp of the app.
    # set the thread as daemon, so that it exits if main app quits.
    p2 = threading.Thread(target=reporter.run, args=(setup,))
    p2.daemon = True
    p2.start()

    # Starting Result Fetcher
    # make a thread that will check if result checker needs to be initiated.
    # set the thread as daemon, so that it exits if main app quits.
    p3 = threading.Thread(target=check_if_fetcher_needs_to_turn_on, args = (whatsApp, ))
    p3.daemon = True
    p3.start()

    # wait for result checker to return success on all the results that are needed to be found.
    p1.join()
    # checker has found the result, update reporter's metadata to False so that reporter quits in the next run.
    with open(setup['paths']['reporter_data'], 'w') as file:
        file.write(str(False))
    # wait for reporter to stop all processes and merge with this thread.
    p2.join()
    # wait for result fetcher to stop all processes and merge with this thread.
    p3.join()

    # send a goodbye message through whatsapp.
    whatsApp.cycle_send_all('Everything Done, I am going to sleep, See ya all next sem!\n\nGoodnight!\n\nP.S. If you want to help improve this bot, go to https://tiny.one/as-gh')