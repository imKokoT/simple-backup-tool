from core.module import Module
from .body import *


class PackerModule(Module):
    name = 'packer'
    description = 'Pack files from scancache into archive'

    def run(self):
        super().run()

        entry()

    def registerCommandArguments(self):
        ...
