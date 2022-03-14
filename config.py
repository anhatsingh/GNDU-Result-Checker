import time, os, json

f = open('secret.json')
key = json.load(f)
key = key['tiny_url_api']
f.close()

setup = {
    'checker_recheck_time': 20*60,      # in seconds    
    'greeting': False,
    'tinyurl_api': key,

    'spreadsheet_name': '(Z_APP_GENERATED) Result_Sem3',
    'make_new_spreadsheet': False,

    'whatsapp_chats': {
            'result_found_send_at': ['Copy-cats', 'A Students'],
            'report_at': ['Logger']
    },

    'checker': {
        'url' : 'https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULT.aspx',
        'department': [1703, 1702],
        'year': 2021,
        'month': 12
    },

    'reporter': {
        'run': True,
        'sleep_time':  6*60*60          # send report every this much seconds
    },

    'fetcher': {
        'sleep_time_for_partial_result': 10*60,                 #in seconds
        '1703':
            {
            'name': 'B.Tech. CSE Section A & B',
            'rollNumberToCrawl': [17032001507,17032001510,17032007422,17032007456,17032007452,17032007444,17032007430],
            'Year': 2021,
            'Month': 12,
            'CourseCode': 1703,
            'Semester': 3,
            'iniRoll': 17032000301,
            'totalStu': 230,
            'numberofsubjects': 5,
            'sheetTitle': 'Section A and B',
            'ResultPage' : 'https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULT.aspx',
            'DisplayPage': 'https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULTDISPLAY.aspx'
        },
        '1702':
            {
            'name': 'B.Tech. CS Section C',
            'rollNumberToCrawl': [],
            'Year': 2021,
            'Month': 12,
            'CourseCode': 1702,
            'Semester': 3,
            'iniRoll': 17022000301,
            'totalStu': 52,
            'numberofsubjects': 5,
            'sheetTitle': 'Section C',
            'ResultPage' : 'https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULT.aspx',
            'DisplayPage': 'https://collegeadmissions.gndu.ac.in/studentArea/GNDUEXAMRESULTDISPLAY.aspx'
        }
    },

    'paths': {
        'reporter_data': os.path.join(os.getcwd(), 'metadata/reporter.txt'),
        'fetcher_data': os.path.join(os.getcwd(), 'metadata/fetcher.txt'),
        'checker_data': os.path.join(os.getcwd(), 'metadata/check.txt'),
        'sheets_data': os.path.join(os.getcwd(), 'metadata/sheets.txt'),
    },
    
}
greeting_msg = f'Hey everyone,\nI am a BOT (v4.3)\n\nI will check whether our Semester {setup["fetcher"]["1703"]["Semester"]} result is uploaded or not, and will inform you all as soon as it is!\n\nI am brand new so I may not work properly and will be getting regular updates :P.\n\nI will be back as soon as I find the result.\nBbieeee!\n\nP.S. If you want to help improve me, go to https://github.com/anhatsingh/GNDU-Result-Checker'