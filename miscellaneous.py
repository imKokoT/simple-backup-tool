import sys
import shutil
from config import *


def updateProgressBar(percentage):
    bar_length = shutil.get_terminal_size().columns - 8
    blocks = int(percentage * bar_length)
    progress_bar = "█" * blocks + "░" * (bar_length - blocks)
    sys.stdout.write(f"\r  {int(percentage * 100)}%  {progress_bar}")
    sys.stdout.flush()


def getTMP():
    if DEBUG:
        if not os.path.exists('./debug'): os.mkdir('./debug')
        if not os.path.exists('./debug/tmp'): os.mkdir('./debug/tmp')
        return './debug/tmp'
    else:
        raise NotImplementedError() 