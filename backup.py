import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
from cloud import getStorageQuota
from properties import *
from logger import logger
import schema
import packer
import archiver
from cloud.clean import deleteAllNotSharedServiceArchives, cleanup
from cloud.authenticate import authenticate
from cloud.drive import send, getDestination, sendMeta
from miscellaneous.miscellaneous import getTMP, humanSize
import miscellaneous.miscellaneous as miscellaneous
import encryptor
from runtime_data import rtd


def backup(archiveName:str, creds:Credentials):
    logger.info('preparing backup to send to cloud...')

    schema:dict = rtd['schema']
    tmp = getTMP()
    schemaName = schema['__name__']

    if not schema.get('destination'):
        logger.fatal(f'failed to get "destination" from schema')
        exit(1)

    try:
        logger.info('building service')
        rtd['service'] = build('drive', 'v3', credentials=creds)

        if schema['__secret_type__'] == 'service' and not schema.get('root'):
            logger.fatal(f'service cannot differentiate between accounts; you must define "root" parameter in schema with targeting shared folder id')
            exit(1)

        if schema['__secret_type__'] == 'service':
            deleteAllNotSharedServiceArchives()

        quota = getStorageQuota(rtd['service'])
        logger.info(f'storage quota: limit={humanSize(quota['limit'])}, usage={humanSize(quota['usage'])}')

        destinationFolder = getDestination(schema['destination'], schema.get('root'))
        
        cleanup(destinationFolder, schemaName)
        logger.info(f'storage quota after cleanup: limit={humanSize(quota['limit'])}, usage={humanSize(quota['usage'])}')

        logger.info('sending backup to cloud...')
        send(f'{tmp}/{archiveName}', f'{schemaName}.archive', destinationFolder)
        sendMeta(destinationFolder)
        
        quota = getStorageQuota(rtd['service'])
        logger.info(f'storage quota after sending: limit={humanSize(quota['limit'])}, usage={humanSize(quota['usage'])}')
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
    
    creds = authenticate()

    packer.packAll()
    
    archName = archiver.archive()

    archName = encryptor.encrypt(archName)

    backup(archName, creds)

    miscellaneous.clean(archName)


if __name__ == '__main__':
    import sys
    import argparse
    if len(sys.argv) == 1:
        print(f'Welcome to SBT!  V{VERSION}')
        print(f'this script create backup from your backup schema\n'
              f' - backup.py <schema name> -> make backup from schema')
    else:
        logger.debug(f'{VERSION=} {DEBUG=}')
        parser = argparse.ArgumentParser()
        parser.add_argument('schema_name',  type=str, help='name of schema')
        parser.add_argument('-sp', '--schema-path', action='store_true', help='use schema name as path of external schema; external schema can include app schemas', required=False)
        args = parser.parse_args()
        createBackupOf(
            args.schema_name,
            schemaPath = args.schema_path
        )
        