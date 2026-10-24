#!/usr/bin/env python3
from properties import VERSION, DEBUG
import core.logger as logger
from core.manage import parseArgs
import sys


def main():
    """
    It's command-line entry point of the tool.

    Run this script within arguments to backup/restore data,
    creating templates, automate processes etc.
    """
    logger.init()
    logger.logging.debug(f'v{VERSION} | {DEBUG=}')
    
    parseArgs(sys.argv)


if __name__ == '__main__':
    main()
