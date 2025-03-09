import os
from schema import getBackupSchema
from properties import *
from archive.internal import *
from archive.external import *
from miscellaneous import getTMP
from runtime_data import rtd


def archive() -> str:
    '''returns archive name'''
    tmp = getTMP()

    schema:dict = rtd['schema']
    schemaName = schema['__name__']
    mode = schema.get('mode', 'internal')
    program = schema.get('program', '7z')

    if mode == 'internal':
        try:
            match schema.get('compressFormat'):
                case 'gz':
                    return gz_archiver.compress(f'{tmp}/{schemaName}.tar', schema)
                case 'bz2':
                        return bz2_archiver.compress(f'{tmp}/{schemaName}.tar', schema)
                case 'zip':
                    return zip_archiver.compress(f'{tmp}/{schemaName}.tar', schema)
                case None | 'tar':
                    return f'{schemaName}.tar'
                case _:
                    logger.fatal(f'unsupported compression format {schema.get('compressionFormat', None)}')
                    exit(1)        
        except ModuleNotFoundError as e:
            logger.fatal(f'module not found; you should to install it; error: {e}')
            exit(1)
    elif mode == 'external':
        match program:
            case '7z':
                return sevenZ_archiver.compress(f'{tmp}/{schemaName}.tar', schema)
            case 'zpaq':
                return zpaq_archiver.compress(f'{tmp}/{schemaName}.tar', schema)
            case _:
                logger.fatal(f'unknown program {program} for external mode')
                exit(1)
    elif mode == 'custom':
        return custom_archiver.compress(f'{tmp}/{schemaName}.tar', schema)
    else:
        logger.fatal(f'unknown mode {mode}')
        exit(1)


def dearchive(schema:dict) -> str:
    '''returns pack name'''
    tmp = getTMP()

    schemaName = schema['__name__']
    mode = schema.get('mode', 'internal')
    program = schema.get('program', '7z')

    downloaded = os.path.join(tmp, f'{schemaName}.downloaded')

    if mode == 'internal':
        try:
            match schema.get('compressFormat'):
                case 'gz':
                    return gz_archiver.decompress(downloaded, schema, schemaName)
                case 'bz2':
                    return bz2_archiver.decompress(downloaded, schema, schemaName)
                case 'zip':
                    return zip_archiver.decompress(downloaded, schema, schemaName) 
                case None | 'tar':
                    if os.path.exists(os.path.join(tmp, f'{schemaName}.tar')):
                        os.remove(os.path.join(tmp, f'{schemaName}.tar'))

                    os.rename(downloaded, os.path.join(tmp, f'{schemaName}.tar'))
                    
                    return f'{schemaName}.tar'
                case _:
                    logger.fatal(f'unsupported compression format {schema.get('compressionFormat', None)}')
                    exit(1)
        except ModuleNotFoundError as e:
            logger.fatal(f'module not found; you should to install it; error: {e}')
            exit(1)
        except ValueError as e:
            logger.fatal(f'dearchive failed; possibly wrong password! error: {e}')
    elif mode == 'external':
        match program:
            case '7z':
                return sevenZ_archiver.decompress(downloaded, schema, schemaName) 
            case 'zpaq':
                return zpaq_archiver.decompress(downloaded, schema)
            case _:
                logger.fatal(f'unknown program "{program}" for external mode')
                exit(1)
    elif mode == 'custom':
        return custom_archiver.decompress(downloaded, schema)
    else:
        logger.fatal(f'unknown mode {mode}')
        exit(1)
