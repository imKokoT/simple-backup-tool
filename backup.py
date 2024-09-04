import yaml
import os
import colorama
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import *


def authenticate():
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
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    programLogger.info('success!')
    return creds


def getBackupSchema(backupName:str) ->dict|None:
    if not os.path.exists('./configs/schemas.yaml'):
        return None
    
    data:dict
    with open('./configs/schemas.yaml', 'r') as f:
        data = yaml.safe_load(f)

    schema = data.get(backupName,None)
    return schema


def createBackupOf(backupName:str):
    schema = getBackupSchema(backupName)
    if not schema:
        programLogger.error(f'No backup schema with name "{backupName}"')
        return
    
    creds = authenticate()
    



if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print(f'this script create backup from your backup schema\n'
              f' - backup.py <schema name> -> make backup from schema')
    else:
        createBackupOf(sys.argv[1])