import yaml
import os
import colorama
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from config import *
import schema
import packer
import archiver


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


def backup(archiveName:str, schema:dict, creds:Credentials):
    programLogger.info('preparing backup to send to cloud...')

    if DEBUG:
        if not os.path.exists('./debug'): os.mkdir('./debug')
        if not os.path.exists('./debug/tmp'): os.mkdir('./debug/tmp')
        tmp = './debug/tmp'

    try:
        programLogger.info('building service')
        service = build('drive', 'v3', creds)

        

    except HttpError as e:
        programLogger.fatal(f'failed to backup; error: {e}')
        exit(1)



def createBackupOf(schemaName:str):
    sch = schema.getBackupSchema(schemaName)
    if not sch:
        programLogger.error(f'No backup schema with name "{schemaName}"')
        return
    
    creds = authenticate()

    packer.packAll(schemaName)
    
    archName = archiver.archive(schemaName)


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print(f'this script create backup from your backup schema\n'
              f' - backup.py <schema name> -> make backup from schema')
    else:
        createBackupOf(sys.argv[1])