import os
import sys
import shutil
import app_config
from logger import logger
from properties import *
from runtime_data import rtd


def updateProgressBar(percentage:float, end:bool=False):
    '''if percentage is None or end is true, progress bar will finish with 100%'''
    percentage = 1 if percentage is None else (1 if percentage > 1 else percentage)

    bar_length = shutil.get_terminal_size().columns - 8
    blocks = int(percentage * bar_length)
    progress_bar = "█" * blocks + "░" * (bar_length - blocks)
    sys.stdout.write(f"\r  {int(percentage * 100)}%  {progress_bar}")
    sys.stdout.flush()

    if end:
        updateProgressBar(percentage=1)
        return
    if percentage >= 1:
        print()


def iprint(*strings):
    '''inline print'''
    sys.stdout.write(f'\r{' '.join(strings)}')
    sys.stdout.flush()


def getTMP():
    '''returns temporal folder of SBT with creating important folders if need'''
    if DEBUG:
        if not os.path.exists('./debug'): os.mkdir('./debug')
        if not os.path.exists('./debug/tmp'): os.mkdir('./debug/tmp')
        return './debug/tmp'
    else:
        raise NotImplementedError('for now works only with DEBUG=True!')


def getRestoreFolder():
    '''returns restore folder of SBT with creating important folders if need'''
    tmp = getTMP()
    p = f'{tmp}/{rtd['schema']['__name__']}'
    if not os.path.exists(p): os.mkdir(p)
    return p


def humanSize(sizeBytes):
    if not app_config.Config().human_sizes:
        return f'{sizeBytes}B'
    if sizeBytes == 0:
        return '0B'
    size_units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = int((len(str(sizeBytes)) - 1) / 3)
    readable_size = sizeBytes / (1024 ** unit_index)
    return f"{readable_size:.2f}{size_units[unit_index]}"


def clean(fname:str):
    tmp = getTMP()
    path = f'{tmp}/{fname}'

    if os.path.basename(fname).split('.')[-1] == 'tar':
        return

    logger.info(f'cleaning "{path}"')

    if not os.path.exists(path):
        logger.error(f'"{path}" not exists')
        return

    os.remove(path)


def catchCritical(func):
    '''logging decorator for catching critical exceptions from root functions'''
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.critical(f'process fall with critical error: {e};\nPlease write issue to github!', exc_info=DEBUG)
            raise
    return wrapper
