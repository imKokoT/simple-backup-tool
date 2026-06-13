from core.config_registry import D
from core.module import Module
from .body import *
from .encryption_stream import EncryptionStream


class CryptographyModule(Module):
    name = 'cryptography'
    description = 'Cryptography module that provide tools for pack encryption/decryption'

    supportedAlgorithms = [
        'aes',
    ]
    encryptionStream = EncryptionStream

    def entry(self):
        raise NotImplementedError()

    def registerCommandArguments(self):
        ...

    def registerSchemaParams(self):
        self.schema_config_registry.register(
            name='encryption',
            type=str,
            default=None,
            description=D('With what algorithm the pack will be encrypted; values: {values}',
                          values=self.supportedAlgorithms),
            validator=lambda x: x in self.supportedAlgorithms
        )
