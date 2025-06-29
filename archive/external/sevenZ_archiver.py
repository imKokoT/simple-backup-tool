import os
from app_config import Config
from logger import logger
from properties import *
from . import tools
from runtime_data import rtd


def _maskPsw(command:list) -> list:
    masked = command.copy()
    psw = [e for e in command if e.startswith('-p')]
    if len(psw) > 0:
        masked.remove(psw[0])
        if Config().hide_password_len:
            psw[0] =  '-p...'
        else:
            psw[0] = '-p' + '*' * len(psw[0])
        masked.extend(psw)        
    return masked


def compress(targetPath:str) -> str:
    schema:dict = rtd['schema']

    compressLevel = schema.get('compressLevel', 5)
    password = schema.get('password')
    args = schema.get('c_args')
    # TODO: remove in 0.11a -----------------------------------------
    if not args:
        args = schema.get('args')
        if args:
            logger.warning(f'"args" parameter in schema {schema['__name__']} deprecated and will be removed in 0.11a! use c_args instead')
    # ---------------------------------------------------------------
    match schema.get('compressFormat', '7z'):
        case '7z': compressFormat = '7z'
        case 'zip': compressFormat = 'zip'
        case 'bz2': compressFormat = 'bzip2'
        case 'gz': compressFormat = 'gzip'
        case 'xz': compressFormat = 'xz'
        case _:
            logger.fatal(f'compression format {schema.get('compressFormat', '7z')} not supports in 7z or in this tool')
            exit(1)

    zipPath = f'{targetPath}.{schema.get('compressFormat', '7z')}'
    if os.path.exists(zipPath):
        os.remove(zipPath)
    logger.info(f'{schema.get('compressFormat', '7z')} with 7z subprocess compressing...')
    
    command = ['7z', 'a', '-y', f'-t{compressFormat}', f'-mx={compressLevel}', zipPath, targetPath]
    if password:
        if schema.get('compressFormat', '7z') == '7z':
            command.append(f'-p{password}')
            command.append('-mhe=on')
        elif schema.get('compressFormat', '7z') == 'zip':
            command.append(f'-p{password}')
            command.append('-mem=AES256')
        else:
            logger.warning(f'7z not supports password for "{schema.get('compressFormat', '7z')}". archive will not encrypted')
    if args:
        command.extend(args)

    logger.info(f'command line: {' '.join(_maskPsw(command))}')
    tools.run(command[0], command)

    return os.path.basename(zipPath)


def decompress(archPath:str, schemaName:str) -> str:
    schema:dict = rtd['schema']
    args = schema.get('d_args')

    logger.info('7z subprocess decompressing...')

    exportPath = f'{os.path.dirname(archPath)}/{schemaName}.tar'
    password = schema.get('password')
    command = ['7z', 'x', '-y', archPath, f'-o{os.path.dirname(exportPath)}']
    if args:
        command.extend(args)
    if password:
        command.append(f'-p{password}')

    logger.info(f'command line: {' '.join(_maskPsw(command))}')
    tools.run(command[0], command)

    return os.path.basename(exportPath)
