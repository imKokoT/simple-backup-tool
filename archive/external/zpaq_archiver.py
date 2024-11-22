import os
import subprocess
from app_config import Config
from logger import logger
from properties import *
import sys


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


def compress(targetPath:str, sch:dict) -> str:
    compressLevel = sch.get('compressLevel', 5)
    password = sch.get('password')
    args = sch.get('args')
    compressFormat = sch.get('compressFormat', 'zpaq')
    if compressFormat != 'zpaq':
        logger.fatal(f'compression format "{sch['compressFormat']}" not supports in zpaq or in this tool')
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

    result = subprocess.run(command, text=True, stdout=sys.stdout)

    if result.returncode == 0:
        logger.info("compress finished with success!")
    else:
        logger.fatal(f"external process error: {result.stderr}")
        exit(1)

    return os.path.basename(zipPath)


def decompress(archPath:str, sch:dict) -> str:
    logger.info('zpaq subprocess decompressing...')
    schemaName = sch['__name__']

    exportPath = os.path.join(os.path.dirname(archPath), f'{schemaName}.tar')
    password = sch.get('password')
    command = ['zpaq', 'x', archPath, os.path.dirname(exportPath), '-f']
    if password:
        command.extend(('-key', password))

    logger.info(f'command line: {' '.join(_maskPsw(command))}')

    result = subprocess.run(command, text=True, stdout=sys.stdout)

    if result.returncode == 0:
        logger.info("decompress finished with success!")
    else:
        logger.fatal(f"external process error: {result.stderr}")
        exit(1)

    return os.path.basename(exportPath)

