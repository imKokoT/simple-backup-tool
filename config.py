import colorama
import logging
import logging.config
import colorlog
import os
import yaml
from os import path

# --- MAIN -------------------------------------------------------------------
VERSION = '0.3a'
DEBUG = True
SCOPES = ['''https://www.googleapis.com/auth/drive''']

class Config:
    __instance = None

    # settings
    hide_password_len = True
    download_chunk_size = 1024*1024*10

    allow_local_replace = True # if true restored backup will rewrite current local changes, if false will create new folder
    ask_before_replace = True # if true will ask before replace files
    

    def __new__(cls):
        if cls.__instance is None:
            cls.__initialized = False
            cls.__instance = super().__new__(cls)
        return cls.__instance


    def toDict(self) -> dict:
        temp = {}
        for k, value in self.__dict__.items():
            temp[k] = value


    def load():
        if not path.exists('configs/'):
            os.mkdir('configs')
        
        try:
            with open('configs/config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.load(f)
                for k, v in config.items():
                    setattr(Config(), k, v)
        except FileNotFoundError:
            with open('configs/config.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(Config().toDict(), f)
        except yaml.YAMLError as e:
            programLogger.error(f'failed to load config; {e}')
            yn = input(f'{YC}do want to recreate [y/N]{DC}: ')
            if yn.strip().lower() != 'y':
                print('process interrupted...')
                exit(0)
            with open('configs/config.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(Config().toDict(), f)


HIDE_PASSWORD_LEN = True
DOWNLOAD_CHUNK_SIZE = 1024*1024*10

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
programLogger = logging.getLogger('SBT')
programLogger.setLevel(logging.DEBUG)
programLogger.addHandler(_programFileHandler)
_temp = logging.StreamHandler()
_temp.setFormatter(colorlog.ColoredFormatter('%(log_color)s'+BASE_LOGGING_FORMAT, 
                                            reset=True, 
                                            log_colors=BASE_LOG_COLORS))
programLogger.addHandler(_temp)

del _temp