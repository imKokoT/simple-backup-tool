import os
from schema import getBackupSchema
from config import *
from archive.internal import *
from archive.external import *
from miscellaneous import getTMP


def archive(schema:dict) -> str:
    '''returns archive name'''
    tmp = getTMP()

    schemaName = schema['__name__']
    mode = schema.get('mode', 'internal')
    program = schema.get('program', '7z')

    if mode == 'internal':
        match schema.get('compressFormat'):
            case '7z':
                raise NotImplementedError()
            case 'gz':
                return gz_archiver.compress(f'{tmp}/{schemaName}.tar', schema)
            case 'bz':
                raise NotImplementedError()
            case 'bz2':
                try:
                    return bz2_archiver.compress(f'{tmp}/{schemaName}.tar', schema)
                except ModuleNotFoundError:
                    logger.fatal(f'"bz2" module not found; you should install it')
                    exit(1)
            case 'zip':
                return zip_archiver.compress(f'{tmp}/{schemaName}.tar', schema)
            case 'xz':
                raise NotImplementedError()
            case None | 'tar':
                return f'{schemaName}.tar'
            case _:
                logger.fatal(f'unknown compression format {schema.get('compressionFormat', None)}')
                exit(1)        
    elif mode == 'external':
        match program:
            case '7z' | None:
                return sevenZ_archiver.compress(f'{tmp}/{schemaName}.tar', schema) 
            case _:
                logger.fatal(f'unknown program {program} for external mode')
                exit(1)
    elif mode == 'custom':
        raise NotImplementedError()
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
        match schema.get('compressFormat'):
            case '7z':
                raise NotImplementedError()
            case 'gz':
                return gz_archiver.decompress(downloaded, schema, schemaName)
            case 'bz':
                raise NotImplementedError()
            case 'bz2':
                try:
                    return bz2_archiver.decompress(downloaded, schema, schemaName)
                except ModuleNotFoundError:
                    logger.fatal(f'"bz2" module not found; you should install it')
                    exit(1)
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
                logger.fatal(f'unknown compression format {schema.get('compressionFormat', None)}')
                exit(1)
    elif mode == 'external':
        match program:
            case '7z' | None:
                return sevenZ_archiver.decompress(downloaded, schema, schemaName) 
            case _:
                logger.fatal(f'unknown program {program} for external mode')
                exit(1)
    elif mode == 'custom':
        raise NotImplementedError()
    else:
        logger.fatal(f'unknown mode {mode}')
        exit(1)
