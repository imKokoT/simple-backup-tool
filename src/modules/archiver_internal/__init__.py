import sys
from core.module import Module, module_register
from core.pack import Pack
from .body import entry

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from modules.packer import PackerModule 


class ArchiverInternalModule(Module):
    name = 'archiver.internal'
    description = 'Build-in archiver that uses selected archivers from tarfile standard library'
    schemaParams = [
        'packer.archiver',
        'packer.format',
        'packer.level'
    ]

    supportedFormats = {'tar','gz','xz','bz'}
    pack:Pack

    def __init__(self):
        super().__init__()
        
        # Python 3.14+
        if sys.version_info[1] >= 14:
            self.supportedFormats.add('zst')

        # patch packer supportedFormats
        module:PackerModule = module_register.get('packer')
        module.supportedFormats.update(self.supportedFormats)

    def entry(self):
        entry()

    def registerCommandArguments(self):
        ...

    def registerSchemaParams(self):
        ...

    def registerAppConfigs(self):
        ...
