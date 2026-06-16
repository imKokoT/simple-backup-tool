from core.module import Chain, module_register
from core.context import ctx
from core.schema import Schema
from paths import getAppDir


class BackupChain(Chain):
    name = 'backup'
    description = 'Backup chain'
    chian = [
        'scan',
        'packer',
        'cloud'
    ]

    def registerCommandArguments(self):
        self.subparser.add_argument('schema_name', help='schema to load')
        self.subparser.add_argument('-f', '--force', action='store_true', help='force backup')

    def run(self, args):
        ctx.schema = Schema(getAppDir() / 'schemas' / f'{ctx.args.schema_name}.yaml')
        
        module_register.get(self.chian[0]).invoke()
        module_register.get(self.chian[1]).invoke()
        module_register.get(self.chian[2]).invoke()
