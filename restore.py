from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
import encryptor
from miscellaneous.get_input import getPassword, getString
from properties import *
from logger import logger
import schema
from cloud.authenticate import authenticate
from cloud.drive import download, getDestination, tryGetMeta
import archiver
import packer
from miscellaneous.miscellaneous import getTMP
import miscellaneous.miscellaneous as miscellaneous
from runtime_data import rtd


def restore(creds:Credentials):
    logger.info('preparing for restore from cloud...')

    tmp = getTMP()
    schema:dict = rtd['schema']
    schemaName = schema['__name__']

    if not schema.get('destination'):
        logger.fatal(f'failed to get "destination" from schema')
        exit(1)
    
    downloadedName = f'{schemaName}.downloaded'

    try:
        logger.info('building service')
        rtd['service'] = build('drive', 'v3', credentials=creds)
        
        if schema['__secret_type__'] == 'service' and not schema.get('root'):
            logger.fatal(f'service cannot differentiate between accounts; you must define "root" parameter in schema with targeting shared folder id')
            exit(1)

        destinationFolder = getDestination(schema['destination'], schema.get('root'))

        meta = tryGetMeta(destinationFolder, schemaName)
        if meta:
            _updateSchema(meta)

        logger.info('getting backup from cloud...')

        download(f'{tmp}/{downloadedName}', f'{schemaName}.archive', destinationFolder)
    except HttpError as e:
        logger.fatal(f'failed to restore; error: {e}')
        exit(1)
    except RefreshError as e:
        logger.fatal(f'failed to restore; error: {e}')
        exit(1)

    logger.info(f'successfully downloaded "{schemaName}.archive" from cloud; it placed in {f'{tmp}/{schemaName}.downloaded'}')


def _updateSchema(meta):
    schema:dict = rtd['schema']

    for k, v in meta.items():
        if k == 'password' and v and not schema.get('password'):
            schema['password'] = getPassword('Archive encrypted with password; enter password:')
        elif k == 'encryption':
            if v != schema.get('encryption'):
                logger.warning(f'meta.encryption={v}, but schema.encryption={schema.get('encryption')}; meta\'s value taken')
                schema['encryption'] = v
            if not schema.get('_enc_keyword'):
                schema['_enc_keyword'] = getPassword(f'Archive encrypted with "{meta['encryption']}"; enter password:')
        else:
            schema[k] = v


def restoreFromCloud(schemaNameOrPath:str, **kwargs):
    if not kwargs.get('fromMeta', False):
        if not kwargs.get('schemaPath'):
            sch = schema.getBackupSchema(schemaNameOrPath, skipUnwrap=True)
            if not sch:
                logger.error(f'No backup schema with name "{schemaNameOrPath}"')
                return
        else:
            sch = schema.load(schemaNameOrPath, skipUnwrap=True)
    else:
        destination = kwargs.get('destination')
        if not destination:
            destination = getString('enter backup destination: ')
        sch = dict(destination=destination, password=kwargs.get('password'))
    
    # important to save changes
    rtd.push('schema', sch, overwrite=True)

    creds = authenticate()

    restore(creds)

    encryptor.decrypt()

    archiver.dearchive()

    miscellaneous.clean(f'{sch['__name__']}.downloaded')

    packer.unpackAll()

    logger.info('restore process finished with success!')


if __name__ == '__main__':
    import sys
    import argparse
    if len(sys.argv) == 1:
        print(f'Welcome to SBT!  V{VERSION}')
        print(f'this script restore backup from cloud using your backup schema')
    else:
        logger.debug(f'{VERSION=} {DEBUG=}')
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
