import argparse
import logging
from properties import *
import sys

logger = logging.getLogger(__name__)


def parseArgs(args):
    logger.debug(f'DEBUG MODE ON; v{VERSION}')

    if len(sys.argv) == 1:
        print(f'SBT v{VERSION} | Copyright {C_YEARS} {COPYRIGHT} ({LINK})')
        return
    
    parser = argparse.ArgumentParser()
    
    args = parser.parse_args()
