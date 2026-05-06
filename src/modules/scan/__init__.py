from core.module import Module
from .body import *
import hashlib


class ScanModule(Module):
    name = 'scan'
    description = 'Scan local targets for changes from filesystem'
    schemaParams = [
        'ignore',
        'targets'
    ]
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
