#!/usr/bin/env python3
from properties import VERSION
import logger
from core.manage import parseArgs
from core import app_config
from core import schema
import sys


def main():
    """
    It's command-line entry point of the tool.

    You must run this script within arguments to backup/restore data,
    creating templates, automate processes etc.
    """
    logger.init()
    logger.logging.debug(f'DEBUG MODE ON; v{VERSION}')

    app_config.registerBaseSettings()
    app_config.config.load()
    schema.registerBaseSettings()
    
    parseArgs(sys.argv)


if __name__ == '__main__':
    main()
