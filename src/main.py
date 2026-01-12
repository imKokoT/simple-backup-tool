#!/usr/bin/env python3
import logger
from core.manage import parseArgs
from core.app_config import registerBaseSettings, configRegistry
import sys


def main():
    """
    It's command-line entry point of the tool.

    You must run this script within arguments to backup/restore data,
    creating templates, automate processes etc.
    """
    logger.init()
    registerBaseSettings()
    parseArgs(sys.argv)


if __name__ == '__main__':
    main()
