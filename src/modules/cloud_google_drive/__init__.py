from google.oauth2.credentials import Credentials

from core.module import Module
from .body import *


class CloudGoogleDriveModule(Module):
    name = 'cloud_google_drive'
    description = 'This module provides access to Google Drive'

    SCOPES = ['''https://www.googleapis.com/auth/drive''']
    cred:Credentials
    serviceCred:bool

    def entry(self):
        entry()

    def registerCommandArguments(self):
        ...

    def registerSchemaParams(self):
        ...

    def registerAppConfigs(self):
        ...
