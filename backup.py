import yaml
import os
import colorama
from config import *


def getBackupSchema(backupName:str) ->dict|None:
    if not os.path.exists('./configs/schemas.yaml'):
        return None
    
    data:dict
    with open('./configs/schemas.yaml', 'r') as f:
        data = yaml.safe_load(f)

    schema = data.get(backupName,None)
    return schema
    


def createBackupOf(backupName:str):
    schema = getBackupSchema(backupName)

    if schema:
        pass
    else:
        programLogger.error(f'No backup schema with name "{backupName}"')

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print(f'this script create backup from your backup schema\n'
              f' - backup.py <schema name> -> make backup from schema')
    else:
        createBackupOf(sys.argv[1])