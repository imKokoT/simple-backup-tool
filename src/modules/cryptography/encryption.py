import io
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from core.context import ctx
from core.module import module_register
from core.vfs import VFile
from .keygen import keygen, bytesgen

logger = logging.getLogger(__name__)
VERSION = b'\x01'
MAGIC = b'EPKG'
SALT = 16

class EncryptionStream(io.IOBase):
    def __init__(self, stream:VFile):
        super().__init__()
        self.stream = stream
        self._encryptor = None
        self._module = module_register.get('cryptography')
        self._method:str = ctx.schema.get('encryption')
        self._salt = bytesgen(SALT)
        self._key = keygen(
            ctx.schema.get('password').encode(),
            self._salt
        )

        logger.info(f'initializing encryption stream; method: {self._method.upper()}')

        match self._method:
            case 'aes':
                nonce = bytesgen(12)

                self.stream.write(MAGIC)
                self.stream.write(VERSION)
                self.stream.write(self._salt)
                self.stream.write(nonce)

                encryptor = Cipher(
                    algorithms.AES(self._key),
                    modes.GCM(nonce)
                ).encryptor()

                self._encryptor = encryptor
            case _:
                raise ValueError(f'unsupported encryption method: {self._method}')

    def write(self, data:bytes) -> int:
        encrypted = self._encryptor.update(data)
        self.stream.write(encrypted)
        return len(data)

    def close(self):
        encrypted = self._encryptor.finalize()
        if encrypted:
            self.stream.write(encrypted)

        self.stream.write(self._encryptor.tag)
        self.stream.close()

    def writable(self): return True
    def flush(self): self.stream.flush()
