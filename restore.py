import os
import json
from getpass import getpass
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import *
import schema
from cloud.authenticate import authenticate
from cloud.drive import download, getDestination
import archiver
import packer
from miscellaneous import getTMP
import clean


def tryGetMeta(service, folder:str, schemaName:str) -> dict|None:
    logger.info(f'getting meta...')

    query = f"'{folder}' in parents and name='{schemaName}.meta' and trashed=false"
    response = service.files().list(q=query, spaces='drive').execute()
    files = response.get('files', [])

    if not files:
        return False
    
    metaId = files[0]['id']
    request = service.files().get_media(fileId=metaId).execute()

    return json.loads(str(request,'utf-8'))


def restore(schema:dict, creds:Credentials):
    logger.info('preparing for restore from cloud...')

    tmp = getTMP()
    schemaName = schema['__name__']

    if not schema.get('destination'):
        logger.fatal(f'failed to get "destination" from schema')
        exit(1)
    
    downloadedName = f'{schemaName}.downloaded'

    try:
        logger.info('building service')
        service = build('drive', 'v3', credentials=creds)
        
        destinationFolder = getDestination(service, schema['destination'])

        meta = tryGetMeta(service, destinationFolder, schemaName)
        if meta:
            for k, v in meta.items():
                if k == 'password' and v and not schema.get('password'):
                    schema['password'] = getpass(f'{YC}Archive encrypted with password; enter password: {RC}')
                elif k != 'password':
                    schema[k] = v

        logger.info('getting backup from cloud...')

        download(service, os.path.join(tmp, downloadedName), f'{schemaName}.archive', destinationFolder)
    except HttpError as e:
        logger.fatal(f'failed to backup; error: {e}')
        exit(1)

    logger.info(f'successfully downloaded "{schemaName}.archive" from cloud; it placed in {os.path.join(tmp, f'{schemaName}.downloaded')}')


def restoreFromCloud(schemaNameOrPath:str, **kwargs):
    if not kwargs.get('fromMeta', False):
        if not kwargs.get('schemaPath'):
            sch = schema.getBackupSchema(schemaNameOrPath)
            if not sch:
                logger.error(f'No backup schema with name "{schemaNameOrPath}"')
                return
        else:
            sch = schema.load(schemaNameOrPath)
    else:
        destination = kwargs.get('destination')
        if not destination:
            destination = input(f'{YC}enter backup destination: {DC}')
        sch = dict(destination=destination, password=kwargs.get('password'))
    
    creds = authenticate()

    restore(sch, creds)

    archiver.dearchive(sch)

    clean.clean(f'{sch['__name__']}.downloaded')

    packer.unpackAll(sch)

    logger.info('restore process finished with success!')


if __name__ == '__main__':
    import sys
    import argparse
    if len(sys.argv) == 1:
        print(f'Welcome to SBT!  V{VERSION}')
        print(f'this script restore backup from cloud using your backup schema')
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument('schema_name',  type=str, help='name of schema')
        parser.add_argument('-m', '--restore-from-meta', action='store_true', help='restore backup from meta', required=False)
        parser.add_argument('-d', '--destination', type=str, help='backup archive destination on Google Drive', required=False)
        parser.add_argument('-p', '--password', type=str, help='password of backup archive', required=False)
        parser.add_argument('-sp', '--schema-path', action='store_true', help='use schema name as path of external schema; external schema can include app schemas', required=False)
        args = parser.parse_args()
        restoreFromCloud(args.schema_name,
                        fromMeta=args.restore_from_meta, 
                        destination=args.destination,
                        password=args.password,
                        schemaPath = args.schema_path
                        )
