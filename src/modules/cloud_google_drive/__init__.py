from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource

from core.module import Module
from .body import *


class CloudGoogleDriveModule(Module):
    name = 'cloud_google_drive'
    description = 'This module provides access to Google Drive'
    schemaParams = [
        'credentials',
        'destination'
    ]

    SCOPES = ['''https://www.googleapis.com/auth/drive''']
    creds:Credentials
    serviceCred:bool
    service:Resource

    def entry(self):
        entry()

    def registerCommandArguments(self):
        ...

    def registerSchemaParams(self):
        ...

    def registerAppConfigs(self):
        ...
