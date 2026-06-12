from core.module import Module
from .body import *


class CryptographyModule(Module):
    name = 'cryptography'
    description = 'Cryptography module that provide tools for pack encryption/decryption'

    def entry(self):
        entry()

    def registerCommandArguments(self):
        ...

    def registerSchemaParams(self):
        ...
