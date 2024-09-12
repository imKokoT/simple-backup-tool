import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from config import *


def authenticate() -> Credentials:
    programLogger.info('authorizing...')
    creds = None
    if not os.path.exists('./configs/client-secrets.json'):
        programLogger.error('failed; no OAuth2 client json file secrets "./configs/client-secrets.json"; get it from Google Cloud Console project')
        exit(1)

    if os.path.exists('./configs/token.json'):
        creds = Credentials.from_authorized_user_file('./configs/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            programLogger.info('token expired, refreshing...')
            creds.refresh(Request())
        else:
            programLogger.info('getting token...')
            flow = InstalledAppFlow.from_client_secrets_file('./configs/client-secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('./configs/token.json', 'w') as token:
            token.write(creds.to_json())
    programLogger.info('success!')
    return creds


def send(service, fpath:str, endName:str, folder=None):
    '''
    @param fpath: path to target file
    @param endName: name of file, which will be in cloud
    @param folder: folder where will place the file 

    Send file to cloud
    '''
    meta = {
            'name': endName,
            'parents': [folder]
        }
    media = MediaFileUpload(fpath)
    uploadFile = service.files().create(body=meta, media_body=media, fields='id').execute()
