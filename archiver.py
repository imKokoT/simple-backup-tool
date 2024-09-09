import os
from schema import getBackupSchema
from config import *

def archive(schemaName:str) -> str:
    '''returns archive name'''
    schema = getBackupSchema(schemaName)

    if not schema:
        programLogger.fatal(f'failed to load schema name "{schemaName}"')
        exit(0)
    
    match schema.get('compressFormat', None):
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
