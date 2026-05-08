from core.module import Module
from .body import *
import hashlib


class ScanModule(Module):
    name = 'scan'
    description = 'Scan local targets for changes from filesystem'
    chainArgs = [
        'force'
    ]

    # statistics
    folders:list[str] = []
    foldersFiles:list[tuple[str]] = []
    files:list[str] = []
    included:int = 0
    scanned:int = 0
    ignoredFiles:int = 0
    ignoredFolders:int = 0
    includedSize:int = 0
    scannedSize:int = 0
    scanhash = hashlib.blake2b()

    def run(self):
        super().run()

        entry()

        # cleanup
        self.files.clear()
        self.foldersFiles.clear()
        self.folders.clear()

    def registerCommandArguments(self):
        ...

    def registerSchemaParams(self):
        self.schema_config_registry.register(
            name='targets',
            type=list[str],
            default=None,
            description='Target folders and files in local disk to backup'
        )
        self.schema_config_registry.register(
            name='ignore',
            type=str,
            default='',
            description='Global ignore pattern; highest priority'
        )
