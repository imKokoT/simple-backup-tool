from core.module import Chain, register


class TestChain(Chain):
    name = 'test'
    description = 'I wish this stuff will work...'
    chian = [
        'test_module'
    ]

    def registerCommandArguments(self):
        ...

    def run(self, args):
        register.get(self.chian[0]).run()
