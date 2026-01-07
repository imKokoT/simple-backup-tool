'''global constants'''
from properties import *
import colorama

VERSION = '1.0b1'
DEBUG = True                # dev-only
EXPERIMENTAL = False        # enable experimental features

COPYRIGHT = 'imKokoT'
LINK = '''https://github.com/imKokoT/simple-backup-tool'''
C_YEARS = '2024-2026'

SCOPES = ['''https://www.googleapis.com/auth/drive''']

MAX_SESSION_LOGS = 10
EVENT_UPDATE_DELAY = 0.05 

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
