import sys
import shutil
from config import *


def updateProgressBar(percentage):
    bar_length = shutil.get_terminal_size().columns - 8
    blocks = int(percentage * bar_length)
    progress_bar = "█" * blocks + "░" * (bar_length - blocks)
    sys.stdout.write(f"\r  {int(percentage * 100)}%  {progress_bar}")
    sys.stdout.flush()


def iprint(*strings):
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
    if not Config().human_sizes:
        return f'{sizeBytes}B'
    if sizeBytes == 0:
        return '0B'
    size_units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = int((len(str(sizeBytes)) - 1) / 3)
    readable_size = sizeBytes / (1024 ** unit_index)
    return f"{readable_size:.2f}{size_units[unit_index]}"
