from core.module import Module
from .body import *


class PackerModule(Module):
    name = 'packer'
    description = 'Pack files from scancache into archive'

    def run(self):
        super().run()
        entry()

    def registerCommandArguments(self):
        ...

    def registerSchemaParams(self):
        self.schema_config_registry.register(
            name='packer.archiver',
            type=str,
            default='internal',
            description='Which archiver to use; possible values `internal`, `7z`, `custom`',
            validator=lambda x: x in ('internal', '7z', 'custom')
        )
        self.schema_config_registry.register(
            name='packer.format',
            type=str,
            default='zip'
        )
        self.schema_config_registry.register(
            name='packer.level',
            type=int,
            default=5,
        )
