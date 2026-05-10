from pathlib import Path
from core.config_registry import D
from core.module import Module
from modules.packer.pack_config import PackConfig
from paths import getTmpDir
from .body import *


class PackerModule(Module):
    name = 'packer'
    description = 'Pack files from scancache into archive'

    archiverTypes = ['internal']
    supportedFormats = {}
    archiverModules = [
        'archiver.internal'
    ]

    packPath:Path
    packConfig:PackConfig

    def entry(self):
        self.packPath = getTmpDir() / ctx.schema.name / 'pack'
        self.packConfig = PackConfig()
        entry()

    def registerCommandArguments(self):
        ...

    def registerSchemaParams(self):
        self.schema_config_registry.register(
            name='packer.archiver',
            type=str,
            default='internal',
            description=D('Which archiver to use; possible values: {variant}',
                          variant=lambda: ', '.join(self.archiverTypes)),
            validator=lambda x: x in self.archiverTypes
        )
        self.schema_config_registry.register(
            name='packer.format',
            type=str,
            default='gz',
            description=D('Possible values: {variant}',
                          variant=lambda: ', '.join(self.supportedFormats))
        )
        self.schema_config_registry.register(
            name='packer.level',
            type=int,
            default=5,
        )
