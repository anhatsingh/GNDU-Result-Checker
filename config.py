import time, os, json

# load the tinyurl api key that is saved in a json file.
f = open('secret.json')
key = json.load(f)
key = key['tiny_url_api']
f.close()

setup = {
    # in seconds; after this much time, checker will check if the result is uploaded or not.
    'checker_recheck_time': 20*60,
    # whether to send the greeting message to all whatsapp groups or not.
    'greeting': False,
    # setting the tinyurl api key here.
    'tinyurl_api': key,

    # Name of the Workbook that will be created inside Google Sheets.
    'spreadsheet_name': '(Z_APP_GENERATED) Result_Sem3',
    # whether to create a new sheet, or use the id and url stored in the metadata files.
    'make_new_spreadsheet': False,


    'whatsapp_chats': {
            # send greetings and result found messages to these groups/individuals.
            'result_found_send_at': ['Copy-cats', 'A Students'],
            # send the app reporting status to these groups.
            'report_at': ['Logger']
    },

    # all settings for result checker.
    'checker': {
        # url where the result will be published
        'url' : 'https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULT.aspx',
        # departments for which to check result for.
        'department': [1703, 1702],
        # year for which result to check for.
        'year': 2021,
        # month for which result to check for.
        'month': 12,
        'semester': 3
    },

    # all settings related to status reporter.
    'reporter': {
        # whether to run the reporter or not.
        'run': True,
        # after this much time, a status report is sent to the above mentioned whatsapp groups.
        'sleep_time':  6*60*60          # in seconds
    },

    # all settings related to result fetcher.
    'fetcher': {
        # if result of all students is not found, rerun fetcher after this much time.
        'sleep_time_for_partial_result': 10*60,                 #in seconds
        # details about individual course whose result we have to fetch.
        '1703':
            {
            # name of the course, to be sent along the message on whatsapp.
            'name': 'B.Tech. CSE Section A & B',
            # additional roll numbers to check result for which are not in a sequence of numbers.
            'rollNumberToCrawl': [17032001507,17032001510,17032007422,17032007456,17032007452,17032007444,17032007430],
            # year to fetch the result for.
            'Year': 2021,
            # month to fetch the result for.
            'Month': 12,
            # course code whose result is being fetch.
            'CourseCode': 1703,
            # semester whose result is to be fetched.
            'Semester': 3,
            # first roll number in the sequence of roll numbers whose results are to be fetched.
            'iniRoll': 17032000301,
            # approximate total students whose result is to be fetched.
            'totalStu': 230,    # MUST NOT excede (Number of Actual Students in class) + 10
            # Number of subjects there are in the above semester.
            'numberofsubjects': 5,
            # Title of the sheet to be created inside the Workbook.
            'sheetTitle': 'A and B',
            # url of the page where the result will be announced.
            'ResultPage' : 'https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULT.aspx',
            # url of the page where the result is displayed.
            'DisplayPage': 'https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULTDISPLAY.aspx'
        },
        # same as above.
        '1702':
            {
            'name': 'B.Tech. CE Section C',
            'rollNumberToCrawl': [],
            'Year': 2021,
            'Month': 12,
            'CourseCode': 1702,
            'Semester': 3,
            'iniRoll': 17022000301,
            'totalStu': 52,
            'numberofsubjects': 5,
            'sheetTitle': 'C',
            'ResultPage' : 'https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULT.aspx',
            'DisplayPage': 'https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULTDISPLAY.aspx'
        }
    },

    # full paths of the metadata files that are being used to interchange data between threads. 
    # Are these Thread-Safe? I may change this method of communication in future, but it stays for now.
    'paths': {
        'reporter_data': os.path.join(os.getcwd(), 'metadata/reporter.txt'),
        'fetcher_data': os.path.join(os.getcwd(), 'metadata/fetcher.txt'),
        'checker_data': os.path.join(os.getcwd(), 'metadata/check.txt'),
        'sheets_data': os.path.join(os.getcwd(), 'metadata/sheets.txt'),
    },
    
}

# greeting message to be sent if it is set to True in above settings.
greeting_msg = f'Hey everyone,\nI am a BOT (v4.3)\n\nI will check whether our Semester {setup["fetcher"]["1703"]["Semester"]} result is uploaded or not, and will inform you all as soon as it is!\n\nI am brand new so I may not work properly and will be getting regular updates :P.\n\nI will be back as soon as I find the result.\nBbieeee!\n\nP.S. If you want to help improve me, go to https://github.com/anhatsingh/GNDU-Result-Checker'