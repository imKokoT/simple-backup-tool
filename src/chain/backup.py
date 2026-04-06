from core.module import Chain, register


class BackupChain(Chain):
    name = 'backup'
    description = 'Backup chain'
    chian = [
        'scan'
    ]

    def registerCommandArguments(self):
        self.subparser.add_argument('schema_name', help='schema to load')

    def run(self, args):
        register.get(self.chian[0]).run()
