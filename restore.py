import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from config import *
import schema
from cloud_tools import authenticate, getDestination, download
import archiver


def restore(schemaName:str, schema:dict, creds:Credentials):
    programLogger.info('preparing for restore from cloud...')

    if DEBUG:
        if not os.path.exists('./debug'): os.mkdir('./debug')
        if not os.path.exists('./debug/tmp'): os.mkdir('./debug/tmp')
        tmp = './debug/tmp'
    else:
        raise NotImplementedError()

    if not schema.get('destination'):
        programLogger.fatal(f'failed to get "destination" from schema')
        exit(1)
    
    downloadedName = f'{schemaName}.downloaded'

    try:
        programLogger.info('building service')
        service = build('drive', 'v3', credentials=creds)

        destinationFolder = getDestination(service, schema['destination'])
        
        programLogger.info('getting backup from cloud...')

        download(service, os.path.join(tmp, downloadedName), f'{schemaName}.archive', destinationFolder)


    except HttpError as e:
        programLogger.fatal(f'failed to backup; error: {e}')
        exit(1)

    programLogger.info(f'successfully downloaded "{schemaName}.archive" from cloud; it placed in {os.path.join(tmp, f'{schemaName}.downloaded')}')


def restoreFromCloud(schemaName:str):
    sch = schema.getBackupSchema(schemaName)
    if not sch:
        programLogger.error(f'No backup schema with name "{schemaName}"')
        return
    
    creds = authenticate()

    restore(schemaName, sch, creds)

    packName = archiver.dearchive(schemaName, sch)


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print(f'this script restore backup from cloud using your backup schema\n'
              f' - restore.py <schema name> -> make backup from schema')
    else:
        restoreFromCloud(sys.argv[1])