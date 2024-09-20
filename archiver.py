import os
from schema import getBackupSchema
from config import *

def archive(schemaName:str) -> str:
    '''returns archive name'''
    schema = getBackupSchema(schemaName)

    if not schema:
        programLogger.fatal(f'failed to load schema name "{schemaName}"')
        exit(1)
    
    match schema.get('compressFormat'):
        case '7z':
            raise NotImplementedError()
        case 'gz':
            raise NotImplementedError()
        case 'bz':
            raise NotImplementedError()
        case 'zip':
            raise NotImplementedError()
        case None | 'tar':
            return f'{schemaName}.tar'
        case _:
            programLogger.fatal(f'unknown compression format {schema.get('compressionFormat', None)}')
            exit(1)        


def dearchive(schemaName:str, schema:dict) -> str:
    '''returns pack name'''
    if DEBUG:
        if not os.path.exists('./debug'): os.mkdir('./debug')
        if not os.path.exists('./debug/tmp'): os.mkdir('./debug/tmp')
        tmp = './debug/tmp'
    else:
        raise NotImplementedError()


    downloaded = os.path.join(tmp, f'{schemaName}.downloaded')

    match schema.get('compressFormat'):
        case '7z':
            raise NotImplementedError()
        case 'gz':
            raise NotImplementedError()
        case 'bz':
            raise NotImplementedError()
        case 'zip':
            raise NotImplementedError()
        case None | 'tar':
            if os.path.exists(os.path.join(tmp, f'{schemaName}.tar')):
                os.remove(os.path.join(tmp, f'{schemaName}.tar'))

            os.rename(downloaded, os.path.join(tmp, f'{schemaName}.tar'))
            
            return f'{schemaName}.tar'
        case _:
            programLogger.fatal(f'unknown compression format {schema.get('compressionFormat', None)}')
            exit(1)