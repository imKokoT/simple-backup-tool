import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
from googleapiclient.http import MediaIoBaseUpload
import io
import json
from cloud import getStorageQuota
from cloud.clean import deleteAllNotSharedServiceArchives
from config import *
import schema
import packer
import archiver
from cloud.authenticate import authenticate
from cloud.drive import send, getDestination
from miscellaneous import getTMP, humanSize
import clean


def _cleanup(service, folder:str, schemaName:str):
    logger.info('cleaning old cloud backup if exists...')

    query = f"'{folder}' in parents and (name='{schemaName}.archive' or name='{schemaName}.meta') and trashed=false"
    response = service.files().list(q=query, spaces='drive').execute()
    files = response.get('files', [])

    if files:
        for f in files:
            file_id = f['id']
            service.files().delete(fileId=file_id).execute()


def _sendMeta(service, folder:str, schema:dict):
    logger.info('sending backup meta...')
    stream = io.BytesIO()

    schemaName = schema['__name__']

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


def backup(archiveName:str, schema:dict, creds:Credentials):
    logger.info('preparing backup to send to cloud...')

    tmp = getTMP()
    schemaName = schema['__name__']

    if not schema.get('destination'):
        logger.fatal(f'failed to get "destination" from schema')
        exit(1)

    try:
        logger.info('building service')
        service = build('drive', 'v3', credentials=creds)

        if schema['__secret_type__'] == 'service' and not schema.get('root'):
            logger.fatal(f'service cannot differentiate between accounts; you must define "root" parameter in schema with targeting shared folder id')
            exit(1)

        if schema['__secret_type__'] == 'service':
            deleteAllNotSharedServiceArchives(service, schema)

        quota = getStorageQuota(service)
        logger.info(f'storage quota: total: limit={humanSize(quota['limit'])}, usage={humanSize(quota['usage'])}')

        destinationFolder = getDestination(service, schema['destination'], schema.get('root'))
        
        _cleanup(service, destinationFolder, schemaName)

        logger.info('sending backup to cloud...')
        send(service, os.path.join(tmp, archiveName), f'{schemaName}.archive', destinationFolder)
        _sendMeta(service, destinationFolder, schema)
        
        quota = getStorageQuota(service)
        logger.info(f'storage quota after sending: total: limit={humanSize(quota['limit'])}, usage={humanSize(quota['usage'])}')
    except HttpError as e:
        logger.fatal(f'failed to backup; error: {e}')
        exit(1)
    except RefreshError as e:
        logger.fatal(f'failed to backup; error: {e}')
        exit(1)

    logger.info(f'successfully backup "{archiveName}" to cloud; it placed in '
                f'{schema['root'] if schema.get('root') else ''}/{f'{schema['destination']}/{schemaName}'}.archive')


def createBackupOf(schemaNameOrPath:str, **kwargs):
    if not kwargs.get('schemaPath'):
        sch = schema.getBackupSchema(schemaNameOrPath)
    else:
        sch = schema.load(schemaNameOrPath)

    if not sch:
        logger.error(f'No backup schema with name "{schemaNameOrPath}"')
        return
    
    creds = authenticate(sch)

    packer.packAll(sch)
    
    archName = archiver.archive(sch)

    backup(archName, sch, creds)

    clean.clean(archName)


if __name__ == '__main__':
    import sys
    import argparse
    if len(sys.argv) == 1:
        print(f'Welcome to SBT!  V{VERSION}')
        print(f'this script create backup from your backup schema\n'
              f' - backup.py <schema name> -> make backup from schema')
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument('schema_name',  type=str, help='name of schema')
        parser.add_argument('-sp', '--schema-path', action='store_true', help='use schema name as path of external schema; external schema can include app schemas', required=False)
        args = parser.parse_args()
        createBackupOf(
            args.schema_name,
            schemaPath = args.schema_path
        )
        