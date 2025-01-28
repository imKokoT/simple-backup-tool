from copy import copy
import os
from app_config import Config
from logger import logger
from properties import *
from . import tools


def _maskPsw(args:list) -> list:
    masked = args.copy()
    psw = [e for e in args if e.strip() == '@pwd']
    if len(psw) > 0:
        masked.remove(psw[0])
        if Config().hide_password_len:
            psw[0] =  '...'
        else:
            psw[0] = '*' * len(psw[0])
        masked.extend(psw)        
    return masked 


def compress(targetPath:str, sch:dict) -> str:
    compressLevel = sch.get('compressLevel')
    password = sch.get('password')
    compressFormat = sch.get('compressFormat', 'unknown')
    args = sch.get('c_args')
    program = sch.get('program')
    
    # TODO: remove in 0.11a -----------------------------------------
    if not args:
        args = sch.get('args')
        if args:
            logger.warning(f'"args" parameter in schema {sch['__name__']} deprecated and will be removed in 0.11a! use c_args instead')
    # ---------------------------------------------------------------
    if not program:
        logger.fatal(f'custom mode requires "program" parameter in schema with path to your archiver!')
        exit(1)
    if not args:
        logger.fatal(f'custom mode requires "args" parameter in schema with command line compress arguments!')
        exit(1)

    zipPath = f'{targetPath}.{compressFormat}'
    logger.info(f'Custom archiver "{sch['program']}" subprocess compressing...')

    if os.path.exists(zipPath):
        os.remove(zipPath)

    command = [program] + args

    i = 0
    while i < len(args):
        command[i] = command[i].replace('@iname', targetPath)
        command[i] = command[i].replace('@oname', zipPath)
        if compressLevel:
            command[i] = command[i].replace('@lvl', str(compressLevel))
        if compressFormat:
            command[i] = command[i].replace('@format', compressFormat)
        i += 1
    displayCommand = copy(command)
    i = 0
    while i < len(args):
        if password:
            command[i] = command[i].replace('@pwd', password)
        i += 1

    logger.info(f'command line: {' '.join(_maskPsw(displayCommand))}')
    tools.run(program, command)

    return os.path.basename(zipPath)


def decompress(archPath:str, sch:dict) -> str:
    args = sch.get('d_args')
    password = sch.get('password')
    program = sch.get('program')
    if not program:
        logger.fatal(f'custom mode requires "program" parameter in schema with path to your archiver!')
        exit(1)
    if not args:
        logger.fatal(f'custom mode requires "args" parameter in schema with command line decompress arguments!')
        exit(1)

    logger.info(f'Custom archiver "{sch['program']}" subprocess decompressing...')
    schemaName = sch['__name__']

    exportPath = os.path.join(os.path.dirname(archPath), f'{schemaName}.tar')
    command = [program] + args

    i = 0
    while i < len(args):
        command[i] = command[i].replace('@iname', archPath)
        command[i] = command[i].replace('@oname', exportPath)
        i += 1
    displayCommand = copy(command)
    i = 0
    while i < len(args):
        if password:
            command[i] = command[i].replace('@pwd', password)
        i += 1

    logger.info(f'command line: {' '.join(_maskPsw(displayCommand))}')
    tools.run(program, command)

    return os.path.basename(exportPath)
