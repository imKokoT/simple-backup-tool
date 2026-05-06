from core.context import ctx
from core.module import Module
from core.schema import Schema
from paths import getAppDir
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
        'schema_name',
        'force'
    ]

    # statistics
    folders:list[str]
    foldersFiles:list[tuple[str]]
    files:list[str]
    included:int
    scanned:int
    ignoredFiles:int
    ignoredFolders:int
    includedSize:int
    scannedSize:int
    scanhash:hashlib.blake2b

    def run(self):
        super().run()
        ctx.schema = Schema(getAppDir() / 'schemas' / f'{ctx.args.schema_name}.yaml')

        # reset stats
        self.scanned = 0
        self.included = 0
        self.includedSize = 0
        self.scannedSize = 0
        self.ignoredFiles = 0
        self.ignoredFolders = 0
        self.folders = []
        self.foldersFiles = []
        self.files = []
        self.scanhash = hashlib.blake2b()

        entry()

        # cleanup
        self.files.clear()
        self.foldersFiles.clear()
        self.folders.clear()

    def registerCommandArguments(self):
        ...
