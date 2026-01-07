#!/usr/bin/env python3
from core.manage import parseArgs
import sys


def main():
    """
    It's command-line entry point of the tool.

    You must run this script within arguments to backup-restore data,
    creating templates, automate processes etc.
    """
    parseArgs(sys.argv)


if __name__ == '__main__':
    main()
