from __future__ import print_function

import os.path, logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
        'https://www.googleapis.com/auth/drive', 
        'https://www.googleapis.com/auth/spreadsheets'
]

logger = logging.getLogger(__name__)

class driveAPI:
    def __init__(self) -> None:
        logger.info('Drive API Initiated')
        self.single_file_id = None
        self.drive = None
    
    def select_file(self, id):
        self.single_file_id = id
        logger.info(f"Setting File ID: {id}")

    def connect(self):
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('drive', 'v3', credentials=creds)
            self.drive = service
            logger.info(f'Connected to Google Drive')

        except HttpError as error:
            logger.exception('Error occurred while trying to connect to Google Drive')

    def share(self):
        def callback(request_id, response, exception):
            if exception:
                logger.error(exception)
            else:
                logger.info(f'Permissions of File {self.single_file_id} changed to {response.get("id")}')

        batch = self.drive.new_batch_http_request(callback=callback)
        user_permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        batch.add(self.drive.permissions().create(
                fileId=self.single_file_id,
                body=user_permission,
                fields='id',
        ))
        batch.execute()
        return True
    
    def search(self):
        page_token = None
        while True:
            response = self.drive.files().list(q="mimeType='application/vnd.google-apps.spreadsheet'",
                                                spaces='drive',
                                                fields='nextPageToken, files(id, name)',
                                                pageToken=page_token).execute()
            for file in response.get('files', []):
                # Process change
                print('Found file: %s (%s)' % (file.get('name'), file.get('id')))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break


if __name__ == "__main__":
    logger.basicConfig(filename='debug.log', level=logger.INFO, format='[%(levelname)s %(asctime)s %(name)s %(process)d %(threadName)s] ' + '%(message)s')
    api = driveAPI()
    api.connect()
    api.select_file('1VjqV7cuoY0UKSz9UrJrnd1gEGh-KF1IfBegzWONLkLY')
    api.share()