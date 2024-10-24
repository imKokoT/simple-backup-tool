import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
import io
import json
from config import *
import schema
import packer
import archiver
from cloud_tools import authenticate, send, getDestination
from miscellaneous import getTMP
import clean


def _cleanup(service, folder:str, schemaName:str):
    programLogger.info('cleaning old cloud backup if exists...')

    query = f"'{folder}' in parents and (name='{schemaName}.archive' or name='{schemaName}.meta') and trashed=false"
    response = service.files().list(q=query, spaces='drive').execute()
    files = response.get('files', [])

    if files:
        for f in files:
            file_id = f['id']
            service.files().delete(fileId=file_id).execute()


def _sendMeta(service, folder:str, schema:dict, schemaName:str):
    programLogger.info('sending backup meta...')
    stream = io.BytesIO()

    data = {
        'compressFormat': schema.get('compressFormat'),
        'password': schema.get('password') is not None,
        'mode': schema.get('mode'),
        'program': schema.get('program')
    }
    meta = {
        'name': f'{schemaName}.meta',
        'parents': [folder],
        'description': f'Meta made by SBT {VERSION}\n'
                       f'see https://github.com/imKokoT/simple-backup-tool'
    }
    stream.write(bytes(json.dumps(data, separators=(',',':')), 'utf-8'))
    media = MediaIoBaseUpload(stream, mimetype='application/octet-stream')

    uploadFile = service.files().create(
        body=meta,
        media_body=media, 
        fields='id'
    ).execute()


def backup(archiveName:str, schemaName:str, schema:dict, creds:Credentials):
    programLogger.info('preparing backup to send to cloud...')

    tmp = getTMP()

    if not schema.get('destination'):
        programLogger.fatal(f'failed to get "destination" from schema')
        exit(1)

    try:
        programLogger.info('building service')
        service = build('drive', 'v3', credentials=creds)

        destinationFolder = getDestination(service, schema['destination'])
        
        _cleanup(service, destinationFolder, schemaName)

        programLogger.info('sending backup to cloud...')
        send(service, os.path.join(tmp, archiveName), f'{schemaName}.archive', destinationFolder)
        _sendMeta(service, destinationFolder, schema, schemaName)
    except HttpError as e:
        programLogger.fatal(f'failed to backup; error: {e}')
        exit(1)

    programLogger.info(f'successfully backup "{archiveName}" to cloud; it placed in {f'{schema['destination']}/{schemaName}'}.archive')



def createBackupOf(schemaName:str):
    sch = schema.getBackupSchema(schemaName)
    if not sch:
        programLogger.error(f'No backup schema with name "{schemaName}"')
        return
    
    creds = authenticate()

    packer.packAll(schemaName)
    
    archName = archiver.archive(schemaName)

    backup(archName, schemaName, sch, creds)

    clean.clean(archName)


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print(f'Welcome to SBT!  V{VERSION}')
        print(f'this script create backup from your backup schema\n'
              f' - backup.py <schema name> -> make backup from schema')
    else:
        createBackupOf(sys.argv[1])
        