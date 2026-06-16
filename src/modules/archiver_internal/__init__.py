import sys
from core.module import Module
from core.pack import Pack
from .body import entry


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

    def entry(self):
        # Python 3.14+
        if sys.version_info[1] >= 14:
            self.supportedFormats.add('zst')

        entry()

    def registerCommandArguments(self):
        ...

    def registerSchemaParams(self):
        ...

    def registerAppConfigs(self):
        ...
