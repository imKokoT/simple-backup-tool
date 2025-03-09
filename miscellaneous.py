import os
import sys
import shutil
import app_config
from logger import logger
from properties import *


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
    if DEBUG:
        if not os.path.exists('./debug'): os.mkdir('./debug')
        if not os.path.exists('./debug/tmp'): os.mkdir('./debug/tmp')
        return './debug/tmp'
    else:
        raise NotImplementedError()


def humanSize(sizeBytes):
    if not app_config.Config().human_sizes:
        return f'{sizeBytes}B'
    if sizeBytes == 0:
        return '0B'
    size_units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = int((len(str(sizeBytes)) - 1) / 3)
    readable_size = sizeBytes / (1024 ** unit_index)
    return f"{readable_size:.2f}{size_units[unit_index]}"


def getFolderPath(skip:bool=True) -> str|None:
    '''get folder path from user'''
    newPath = ''
    while not os.path.exists(newPath) or not os.path.isdir(newPath):
        newPath = input(f'Enter directory path{' or nothing to skip' if skip else ''}: ')
        if newPath.strip() == '' and skip:
            return
        if not os.path.exists(newPath) or not os.path.isdir(newPath):
            print(f'{RC}invalid path "{newPath}"!')
    
    return newPath


class Singleton(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            instance = super().__call__(*args, **kwargs)
            cls.__instances[cls] = instance
            if hasattr(cls, 'onInstanceCreated') and callable(getattr(cls, 'onInstanceCreated')):
                cls.onInstanceCreated()
        return cls.__instances[cls]


def clean(fname:str):
    tmp = getTMP()
    path = os.path.join(tmp, fname)

    if os.path.basename(fname).split('.')[-1] == 'tar':
        return

    logger.info(f'cleaning "{path}"')

    if not os.path.exists(path):
        logger.error(f'"{path}" not exists')
        return

    os.remove(path)
