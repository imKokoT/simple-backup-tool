import io
from pathlib import Path

from core.config_registry import D
from core.module import Module
from core.pack import PackConfig
from paths import getTmpDir
from .body import *

class UnpackerModule(Module):
    name = 'unpacker'
    description = 'This module opens local pack and restores it\'s content'

    packPath:Path
    packConfig:PackConfig
    packStream:io.IOBase

    def entry(self):
        self.packPath = getTmpDir() / ctx.schema.name / 'pack'
        self.packConfig = PackConfig()
        self.packConfig.schema = ctx.schema
        entry()

    def registerCommandArguments(self):
        ...

    def registerSchemaParams(self):
        ...

    def registerAppConfigs(self):
        ...
