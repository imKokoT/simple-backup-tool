from tarfile import TarFile
from core.module import Module
from .body import entry


class ArchiverInternalModule(Module):
    name = 'archiver.internal'
    description = 'Build-in archiver that uses selected archivers from tarfile standard library'
    schemaParams = [
        'packer.archiver',
        'packer.format',
        'packer.level'
    ]

    supportedFormats = {'tar','gz','xz','bz','zst'}
    pack:TarFile

    def entry(self):
        entry()

    def registerCommandArguments(self):
        ...

    def registerSchemaParams(self):
        ...
