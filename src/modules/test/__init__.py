from core.module import Module
from . import body


class TestModule(Module):
    name = 'test_module'
    description = 'this is test module'

    def run(self):
        body.test()

    def registerCommandArguments(self):
        self.argGroup.add_argument('--option', action='store_true', help='testing module option')

    def registerSchemaParams(self):
        ...
