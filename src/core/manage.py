from properties import *
from core.module import register
import argparse
import logging
import sys

logger = logging.getLogger(__name__)


def parseArgs(args):
    if len(sys.argv) == 1:
        print(f'SBT v{VERSION} | Copyright {C_YEARS} {COPYRIGHT} ({LINK})')
        return
    
    parser = argparse.ArgumentParser()
    
    # register modules

    # init chains
    chains = [
        
        ]

    args = parser.parse_args()
    args.func(args)
