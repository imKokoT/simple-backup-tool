import os
from config import *


def restoreFromCloud(schemaName:str):
    pass


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print(f'this script restore backup from cloud with your backup schema\n'
              f' - restore.py <schema name> -> make backup from schema')
    else:
        restoreFromCloud(sys.argv[1])