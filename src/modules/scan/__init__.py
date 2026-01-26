from core.context import ctx
from core.module import Module
from core.schema import Schema, schema_config_registry
from paths import getAppDir
from .body import *


class ScanModule(Module):
    name = 'scan'
    description = 'Scan filesystem for changes'

    def run(self):
        ctx.schema = Schema(getAppDir() / 'schemas' / f'{ctx.args.schema_name}.yaml')
        scan()

    def registerCommandArguments(self):
        ...

    def requireSchemaParams(self):
        schema_config_registry.require('ignore')
        schema_config_registry.require('targets')
