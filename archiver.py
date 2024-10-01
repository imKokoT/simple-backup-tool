import os
from schema import getBackupSchema
from config import *
from archive.internal import *
from tools import getTMP


def archive(schemaName:str) -> str:
    '''returns archive name'''
    schema = getBackupSchema(schemaName)

    tmp = getTMP()

    if not schema:
        programLogger.fatal(f'failed to load schema name "{schemaName}"')
        exit(1)
    
    match schema.get('compressFormat'):
        case '7z':
            raise NotImplementedError()
        case 'gz':
            return gz_archiver.compress(f'{tmp}/{schemaName}.tar', schema)
        case 'bz':
            raise NotImplementedError()
        case 'bz2':
            return bz2_archiver.compress(f'{tmp}/{schemaName}.tar', schema)
        case 'zip':
            return zip_archiver.compress(f'{tmp}/{schemaName}.tar', schema)
        case 'xz':
            raise NotImplementedError()
        case None | 'tar':
            return f'{schemaName}.tar'
        case _:
            programLogger.fatal(f'unknown compression format {schema.get('compressionFormat', None)}')
            exit(1)        


def dearchive(schemaName:str, schema:dict) -> str:
    '''returns pack name'''
    tmp = getTMP()

    downloaded = os.path.join(tmp, f'{schemaName}.downloaded')

    match schema.get('compressFormat'):
        case '7z':
            raise NotImplementedError()
        case 'gz':
            return gz_archiver.decompress(downloaded, schema, schemaName)
        case 'bz':
            raise NotImplementedError()
        case 'bz2':
            return bz2_archiver.decompress(downloaded, schema, schemaName)
        case 'zip':
            return zip_archiver.decompress(downloaded, schema, schemaName) 
        case 'xz':
            raise NotImplementedError()
        case None | 'tar':
            if os.path.exists(os.path.join(tmp, f'{schemaName}.tar')):
                os.remove(os.path.join(tmp, f'{schemaName}.tar'))

            os.rename(downloaded, os.path.join(tmp, f'{schemaName}.tar'))
            
            return f'{schemaName}.tar'
        case _:
            programLogger.fatal(f'unknown compression format {schema.get('compressionFormat', None)}')
            exit(1)
            