import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from config import *
import schema
from cloud_tools import authenticate


def restore(schemaName:str, schema:dict, creds:Credentials):
    pass


def restoreFromCloud(schemaName:str):
    sch = schema.getBackupSchema(schemaName)
    if not sch:
        programLogger.error(f'No backup schema with name "{schemaName}"')
        return
    
    creds = authenticate()


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print(f'this script restore backup from cloud using your backup schema\n'
              f' - restore.py <schema name> -> make backup from schema')
    else:
        restoreFromCloud(sys.argv[1])