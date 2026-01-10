from chain.test import TestChain
from properties import *
from core.module import register
from modules.test import TestModule
import argparse
import logging
import sys

logger = logging.getLogger(__name__)


def parseArgs(args):
    logger.debug(f'DEBUG MODE ON; v{VERSION}')

    if len(sys.argv) == 1:
        print(f'SBT v{VERSION} | Copyright {C_YEARS} {COPYRIGHT} ({LINK})')
        return
    

    parser = argparse.ArgumentParser()
    
    # register modules
    register.register(TestModule(parser))
    # init chains
    chains = [
        TestChain(parser)
    ]

    args = parser.parse_args()
    args.func(args)
