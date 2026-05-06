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
        ctx.schema = Schema(getAppDir() / 'schemas' / f'{ctx.args.schema_name}.yaml')

        entry()

        # cleanup
        self.files.clear()
        self.foldersFiles.clear()
        self.folders.clear()

    def registerCommandArguments(self):
        ...
