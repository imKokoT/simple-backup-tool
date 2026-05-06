from core.module import Chain, register


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
        register.get(self.chian[0]).run()
