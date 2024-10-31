import logging
import logging.config
import colorlog
import os
from os import path

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
_programFileHandler = logging.FileHandler('logs/program.log', 'w', 'utf-8')
_programFileHandler.setFormatter(logging.Formatter(BASE_LOGGING_FORMAT))

# === Program logger ===
logger = logging.getLogger('SBT')
logger.setLevel(logging.DEBUG)
logger.addHandler(_programFileHandler)
_temp = logging.StreamHandler()
_temp.setFormatter(colorlog.ColoredFormatter('%(log_color)s'+BASE_LOGGING_FORMAT, 
                                            reset=True, 
                                            log_colors=BASE_LOG_COLORS))
logger.addHandler(_temp)

del _temp
