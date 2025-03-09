import datetime
import logging
import logging.config
import colorlog
import os
from os import path
from properties import *


if not path.exists('logs'):
    os.mkdir('logs')

BASE_LOGGING_FORMAT = '[%(asctime)s] %(levelname)s %(name)s: %(message)s'
BASE_LOG_COLORS ={
        'DEBUG': 'light_black',
        'INFO': 'light_black',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
logger = logging.getLogger('SBT')
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

_programFileHandler = logging.FileHandler(
    f'logs/session_{str(datetime.datetime.now().replace(microsecond=0)).replace(':','.')}.log', 
    'w', 'utf-8')
_programFileHandler.setFormatter(logging.Formatter(BASE_LOGGING_FORMAT))
logger.addHandler(_programFileHandler)

_temp = logging.StreamHandler()
_temp.setFormatter(colorlog.ColoredFormatter('%(log_color)s'+BASE_LOGGING_FORMAT, 
                                            reset=True, 
                                            log_colors=BASE_LOG_COLORS))
logger.addHandler(_temp)

if __name__ != '__main__':
    logs = [f'./logs/{l}' for l in os.listdir('./logs') if l.startswith('session')]
    logs.sort(key=lambda x: os.path.getctime(x))

    if len(logs) > MAX_SESSION_LOGS:
        os.remove(logs[0])
