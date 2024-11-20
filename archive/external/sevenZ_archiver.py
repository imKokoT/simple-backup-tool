import os
import subprocess
from app_config import Config
from logger import logger
from properties import *
import sys


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


def compress(targetPath:str, sch:dict) -> str:
    compressLevel = sch.get('compressLevel', 5)
    password = sch.get('password')
    args = sch.get('args')
    match sch.get('compressFormat', '7z'):
        case '7z': compressFormat = '7z'
        case 'zip': compressFormat = 'zip'
        case 'bz2': compressFormat = 'bzip2'
        case 'gz': compressFormat = 'gzip'
        case 'xz': compressFormat = 'xz'
        case _:
            logger.fatal(f'compression format {sch.get('compressFormat', '7z')} not supports in 7z or in this tool')
            exit(1)

    zipPath = f'{targetPath}.{sch.get('compressFormat', '7z')}'
    logger.info(f'{sch.get('compressFormat', '7z')} with 7z subprocess compressing...')
    
    command = ['7z', 'a', '-y', f'-t{compressFormat}', f'-mx={compressLevel}', zipPath, targetPath]
    if password:
        if sch.get('compressFormat', '7z') == '7z':
            command.append(f'-p{password}')
            command.append('-mhe=on')
        elif sch.get('compressFormat', '7z') == 'zip':
            command.append(f'-p{password}')
            command.append('-mem=AES256')
        else:
            logger.warning(f'7z not supports password for "{sch.get('compressFormat', '7z')}". archive will not encrypted')
    if args:
        command.extend(args)

    logger.info(f'command line: {' '.join(_maskPsw(command))}')
    result = subprocess.run(command, text=True, stdout=sys.stdout)

    if result.returncode == 0:
        logger.info("compress finished with success!")
    else:
        logger.fatal(f"external process error: {result.stderr}")
        exit(1)

    return os.path.basename(zipPath)


def decompress(archPath:str, sch:dict, schemaName:str) -> str:
    logger.info('7z subprocess decompressing...')

    exportPath = os.path.join(os.path.dirname(archPath), f'{schemaName}.tar')
    password = sch.get('password')
    command = ['7z', 'x', '-y', archPath, f'-o{os.path.dirname(exportPath)}']
    if password:
        command.append(f'-p{password}')

    logger.info(f'command line: {' '.join(_maskPsw(command))}')
    result = subprocess.run(command, text=True, stdout=sys.stdout)

    if result.returncode == 0:
        logger.info("decompress finished with success!")
    else:
        logger.fatal(f"external process error: {result.stderr}")
        exit(1)

    return os.path.basename(exportPath)
