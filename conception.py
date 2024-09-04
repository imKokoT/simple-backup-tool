import os
import os.path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SCOPES = ['''https://www.googleapis.com/auth/drive''']
creds = None

if os.path.exists('./configs/token.json'):
    creds = Credentials.from_authorized_user_file('./configs/token.json', SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "./configs/client-secrets.json",
            SCOPES
        )
        creds = flow.run_local_server(port=0)

    with open('./configs/token.json', 'w') as f:
        f.write(creds.to_json())

try:
    service = build('drive', 'v3', credentials=creds)

    response = service.files().list(
        q="name='testFolder' and mimeType='application/vnd.google-apps.folder'",
        spaces='drive'
    ).execute()

    if not response['files']:
        file_metadata = {
            'name': "testFolder",
            'mimeType': "application/vnd.google-apps.folder"
        }
        file = service.files().create(body=file_metadata, fields='id').execute()
    
        folder_id = file.get('id')
    else: 
        folder_id = response['files'][0]['id']
    
    # backup here
    backup_metadata = {
        'name': 'backup.txt',
        'parents': [folder_id]
    }

    media = MediaFileUpload('./_tests/backup.txt')
    upload_file = service.files().create(body=backup_metadata, media_body=media, fields='id').execute()

    print('successfully backed up!')

except HttpError as e:
    print(f'service built error: {e}')
