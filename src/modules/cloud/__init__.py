from core.config_registry import D
from core.module import Module
from .body import *


class CloudModule(Module):
    name = 'cloud'
    description = 'This module manages access to a cloud'

    cloudModules = [
        'cloud_google_drive'
    ]

    def entry(self):
        entry()

    def registerCommandArguments(self):
        ...

    def registerSchemaParams(self):
        self.schema_config_registry.register(
            name='destination',
            type=str,
            default=None,
            description='Destination on a cloud, where to send/download a pack',
            required=True
        )
        self.schema_config_registry.register(
            name='credential',
            type=str,
            default=None,
            description='Credential file to access a cloud'
        )
        self.schema_config_registry.register(
            name='cloud',
            type=str,
            default=self.cloudModules[0],
            description=D('What cloud to use; possible values {variant}',
                          variant=', '.join(self.cloudModules)),
            validator=lambda x: x in self.cloudModules
        )

    def registerAppConfigs(self):
        ...
