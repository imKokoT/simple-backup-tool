import os
from pathlib import Path

from core.config_registry import D
from core.module import Module
from core.pack import Pack, PackConfig
from paths import getTmpDir
from .body import *

class UnpackerModule(Module):
    name = 'unpacker'
    description = 'This module opens local pack and restores it\'s content'

    archiverType = [
        'internal'
    ]
    archiverModules = [
        'archiver.internal'
    ]

    restoredFolder:Path
    packPath:Path
    packConfig:PackConfig
    packStream:VFile
    pack:Pack

    def entry(self):
        self.packPath = getTmpDir() / ctx.schema.name / 'pack'
        self.restoredFolder = getTmpDir() / ctx.schema.name / 'restored'
        self.packConfig = PackConfig()
        self.packConfig.schema = ctx.schema

        os.makedirs(self.restoredFolder, exist_ok=True)
        entry()

    def registerCommandArguments(self):
        ...

    def registerSchemaParams(self):
        ...

    def registerAppConfigs(self):
        self.app_config_registry.register(
            'restore.allow_local_replace',
            bool,
            False,
            'Allow replace local files with files from pack; otherwise restored files/folders will have "-restored" suffix'
        )
        self.app_config_registry.register(
            'restore.restore_to_restored_if_path_invalid',
            bool,
            True,
            'Restore to "restored" folder if target path is invalid'
        )
