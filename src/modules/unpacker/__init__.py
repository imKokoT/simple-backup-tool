from core.config_registry import D
from core.module import Module
from .body import *

class UnpackerModule(Module):
    name = 'unpacker'
    description = 'This module opens local pack and restores it\'s content'

    def entry(self):
        entry()

    def registerCommandArguments(self):
        ...

    def registerSchemaParams(self):
        ...

    def registerAppConfigs(self):
        ...
