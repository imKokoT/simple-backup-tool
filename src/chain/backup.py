from core.module import Chain, register
from core.context import ctx
from core.schema import Schema
from paths import getAppDir


class BackupChain(Chain):
    name = 'backup'
    description = 'Backup chain'
    chian = [
        'scan'
    ]

    def registerCommandArguments(self):
        self.subparser.add_argument('schema_name', help='schema to load')
        self.subparser.add_argument('-f', '--force', action='store_true', help='force backup')

    def run(self, args):
        ctx.schema = Schema(getAppDir() / 'schemas' / f'{ctx.args.schema_name}.yaml')
        register.get(self.chian[0]).run()
