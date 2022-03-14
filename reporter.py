import time, logging
from whatsappManager.whatsapp import Whatsapp

logger = logging.getLogger(__name__)

# not working rn, update later
def report_status(whatsApp, setup):
    while(True):
        try:
            run_reporter = open(setup['paths']['reporter_data'])

            if run_reporter.readline().strip() == str(True):
                checker_file = open(setup['paths']['checker_data'])                
                data = checker_file.read()
                whatsApp.cycle_send_all(data)
                time.sleep(setup['reporter']['sleep_time'])
                checker_file.close()
            else:
                break
            run_reporter.close()
        
        except:
            logger.exception('Error occurred while reporting status on whatsapp')


def run(setup):
    if setup['reporter']['run']:
        wa = Whatsapp()
        wa.set_chat(setup['whatsapp_chats']['report_at'])
        wa.set_header(f'Reporter v1\nTime: {time.strftime("%I:%M:%S %p, %d-%m-%Y")}')

        sheets_file = open(setup['paths']['sheets_data'])
        sheets_file.readline()
        wa.cycle_send_all(f'Reporter reporting for duty.\nURL: {sheets_file.readline()}')
        sheets_file.close()

        report_status(wa, setup)
        wa.cycle_send_all('I hope I have performed my duties well. Going to sleep, goodbye.')








if __name__ == '__main__':
    dummy_setup = {
        'whatsapp_chats': {
            'report_at': ['Logger']
        },

        'paths': {
            'checker_data': 'metadata/check.txt',
            'reporter_data': 'metadata/reporter.txt'
        },

        'reporter': {
            'run': True,
            'sleep_time': 5                 # in seconds
        }
    }

    with open(dummy_setup['paths']['reporter_data'], 'w') as file:
        file.write(str(dummy_setup['reporter']['run']))

    run(dummy_setup)