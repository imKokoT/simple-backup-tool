import datetime
from colorlog import ColoredFormatter
from properties import *
import logging
import os

BASE_LOGGING_FORMAT = '\r%(log_color)s[%(asctime)s] %(levelname)s %(name)s: %(message)s%(reset)s'
BASE_FILE_LOGGING_FORMATE = '[%(asctime)s] %(levelname)s %(name)s: %(message)s'
BASE_LOG_COLORS = {
        'DEBUG': 'light_black',
        'INFO': 'light_black',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }


def init():
    """Init logging"""
    colorama.init(autoreset=True)
    os.makedirs('logs', exist_ok=True)
    
    stream = logging.StreamHandler()
    stream.setFormatter(
        ColoredFormatter(
            BASE_LOGGING_FORMAT,
            log_colors=BASE_LOG_COLORS,
        )
    )

    file = logging.FileHandler(
        f'logs/session_{str(datetime.datetime.now().replace(microsecond=0)).replace(':','.')}.log', 
        'w', 'utf-8')
    file.setFormatter(
        logging.Formatter(BASE_FILE_LOGGING_FORMATE)
    )

    root = logging.getLogger()
    root.setLevel(logging.DEBUG if DEBUG else logging.INFO)
    root.addHandler(stream)
    root.addHandler(file)

    # auto clean-up
    logs = [f'./logs/{l}' for l in os.listdir('./logs') if l.startswith('session')]
    logs.sort(key=lambda x: os.path.getctime(x))
    while len(logs) > MAX_SESSION_LOGS:
        os.remove(logs.pop(0))
    