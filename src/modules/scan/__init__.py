from core.context import ctx
from core.module import Module
from core.schema import Schema, schema_config_registry
from paths import getAppDir
from .body import *


class ScanModule(Module):
    name = 'scan'
    description = 'Scan local targets for changes in filesystem' 

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

        entry()

        # cleanup
        self.files.clear()
        self.foldersFiles.clear()
        self.folders.clear()

    def registerCommandArguments(self):
        ...

    def requireSchemaParams(self):
        schema_config_registry.require('ignore')
        schema_config_registry.require('targets')
