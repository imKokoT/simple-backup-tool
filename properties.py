import colorama


# --- MAIN -------------------------------------------------------------------
VERSION = '0.9a'
DEBUG = True
SCOPES = ['''https://www.googleapis.com/auth/drive''']


class Singleton(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            instance = super().__call__(*args, **kwargs)
            cls.__instances[cls] = instance
            if hasattr(cls, 'onInstanceCreated') and callable(getattr(cls, 'onInstanceCreated')):
                cls.onInstanceCreated()
        return cls.__instances[cls]

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
