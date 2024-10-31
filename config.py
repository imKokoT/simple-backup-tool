import colorama
import os
import yaml
from os import path
from logger import logger

# --- MAIN -------------------------------------------------------------------
VERSION = '0.4a'
DEBUG = True
SCOPES = ['''https://www.googleapis.com/auth/drive''']

class Config:
    __instance = None
    __initialized = False

    def __new__(cls):
        if cls.__instance is None:
            cls.__initialized = False
            cls.__instance = super().__new__(cls)
            cls.load()
        return cls.__instance


    def __init__(self):
        if Config.__initialized: return 
        Config.__initialized = True
        # === settings ===
        self.human_sizes = False # if true, byte sizes will print in "B", "KB", "MB", "GB", "TB"

        self.download_chunk_size = 1024*1024*10

        self.allow_local_replace = True # if true restored backup will rewrite current local changes, if false will create new folder
        self.ask_before_replace = True # if true will ask before replace files
        self.include_gitignore = False # if true will include .gitignore files patterns
        self.ask_for_other_extract_path = True # if true will ask for path if failed to unpack folder
        self.restore_to_tmp_if_path_invalid = False # if true will restore target folder or file to tmp/restored

        self.hide_password_len = True
        self.auto_remove_archive = True # if true archives, that was created or downloaded, will be deleted; .tar excluded


    def save():
        if not path.exists('configs/'):
            os.mkdir('configs')

        with open('configs/config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(Config().__dict__, f)


    def load():
        if not path.exists('configs/'):
            os.mkdir('configs')
        
        try:
            with open('configs/config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                for k, v in config.items():
                    setattr(Config(), k, v)
                if config != Config().__dict__:
                    logger.info('updated config.yaml to newer version')
                    Config.save()
        except FileNotFoundError:
            Config.save()
        except yaml.YAMLError as e:
            logger.error(f'failed to load config; {e}')
            yn = input(f'{YC}do you want to recreate config? [y/N]{DC}: ')
            if yn.strip().lower() != 'y':
                print('process interrupted...')
                exit(0)
            Config.save()


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
