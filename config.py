import colorama
import logging
import logging.config
import colorlog
import os
from os import path

# --- MAIN -------------------------------------------------------------------
VERSION = '0.2a'
DEBUG = True
SCOPES = ['''https://www.googleapis.com/auth/drive''']

DOWNLOAD_CHUNK_SIZE = 1024*1024*10
COMPRESS_CHUNK_SIZE = 1024*1024

# --- restore settings -------------------------------------------------------
ALLOW_LOCAL_REPLACE = True # if true restored backup will rewrite current local changes, if false will create new folder
ASK_BEFORE_REPLACE = True # if true will ask before replace files

# --- colorama shortcuts -----------------------------------------------------
colorama.init(autoreset=True) # init colorama escape codes
DC = colorama.Style.RESET_ALL

RC = colorama.Fore.RED
GC = colorama.Fore.GREEN
BC = colorama.Fore.BLUE
YC = colorama.Fore.YELLOW
CC = colorama.Fore.CYAN
BKC = colorama.Fore.BLUE
MC = colorama.Fore.MAGENTA
WC = colorama.Fore.WHITE

LRC = colorama.Fore.LIGHTRED_EX
LGC = colorama.Fore.LIGHTGREEN_EX
LBC = colorama.Fore.LIGHTBLUE_EX
LYC = colorama.Fore.LIGHTYELLOW_EX
LCC = colorama.Fore.LIGHTCYAN_EX
LBKC = colorama.Fore.LIGHTBLACK_EX
LMC = colorama.Fore.LIGHTMAGENTA_EX
LWC = colorama.Fore.LIGHTWHITE_EX

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
programLogger = logging.getLogger('Program')
programLogger.setLevel(logging.DEBUG)
programLogger.addHandler(_programFileHandler)
_temp = logging.StreamHandler()
_temp.setFormatter(colorlog.ColoredFormatter('%(log_color)s'+BASE_LOGGING_FORMAT, 
                                            reset=True, 
                                            log_colors=BASE_LOG_COLORS))
programLogger.addHandler(_temp)

del _temp