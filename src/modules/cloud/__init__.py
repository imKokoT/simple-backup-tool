from core.config_registry import D
from core.module import Module
from .body import *


class CloudModule(Module):
    name = 'cloud'
    description = 'This module manages access to a cloud'

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
