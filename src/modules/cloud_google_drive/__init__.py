from core.config_registry import D
from core.module import Module
from .body import *


class CloudGoogleDriveModule(Module):
    name = 'cloud_google_drive'
    description = 'This module provides access to Google Drive'

    def entry(self):
        entry()

    def registerCommandArguments(self):
        ...

    def registerSchemaParams(self):
        ...

    def registerAppConfigs(self):
        ...
