import os
from app_config import Config
from logger import logger
from properties import *
from . import tools
from runtime_data import rtd


def _maskPsw(command:list) -> list:
    masked = command.copy()
    psw = [e for e in command if e.startswith('-key')]
    if len(psw) > 0:
        masked.remove(psw[0])
        if Config().hide_password_len:
            psw[0] =  '-key ...'
        else:
            psw[0] = '-key ' + '*' * len(psw[0])
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
    compressFormat = schema.get('compressFormat', 'zpaq')
    if compressFormat != 'zpaq':
        logger.fatal(f'compression format "{schema['compressFormat']}" not supports in zpaq or in this tool')
        exit(1)
    
    zipPath = f'{targetPath}.{compressFormat}'
    logger.info(f'"{compressFormat}" with 7z subprocess compressing...')

    if os.path.exists(zipPath):
        os.remove(zipPath)
    command = ['zpaq', 'a', zipPath, targetPath, f'-m{compressLevel}']
    
    if args:
        command.extend(args)
    if password:
        command.extend(('-key', password))

    logger.info(f'command line: {' '.join(_maskPsw(command))}')

    tools.run(command[0], command)

    return os.path.basename(zipPath)


def decompress(archPath:str) -> str:
    schema:dict = rtd['schema']
    args = schema.get('d_args')

    logger.info('zpaq subprocess decompressing...')
    schemaName = schema['__name__']

    exportPath = os.path.join(os.path.dirname(archPath), f'{schemaName}.tar')
    password = schema.get('password')
    command = ['zpaq', 'x', archPath, os.path.dirname(exportPath), '-f']
    if args:
        command.extend(args)
    if password:
        command.extend(('-key', password))

    logger.info(f'command line: {' '.join(_maskPsw(command))}')

    tools.run(command[0], command)

    return os.path.basename(exportPath)

