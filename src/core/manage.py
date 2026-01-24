import modules
from properties import *
from core.module import register
from core.context import ctx
import argparse
import logging
import sys

logger = logging.getLogger(__name__)


def parseArgs(args):
    if len(sys.argv) == 1:
        print(f'SBT v{VERSION} | Copyright {C_YEARS} {COPYRIGHT} ({LINK})')
        return
    
    parser = argparse.ArgumentParser()
    ctx.args = parser.parse_args()
    
    # register modules
    register.register(modules.scan.ScanModule(parser))
    # init chains
    ctx.chains = [

        ]

    args.func(ctx.args)
