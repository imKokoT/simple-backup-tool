from properties import *
import sys

def parseArgs(args):
    if len(sys.argv) == 1:
        print(f'SBT V{VERSION} | Copyright {C_YEARS} {COPYRIGHT} ({LINK})')
