import io
import logging

from core.vfs import VFile
from .backends.aes import AESDecryptionBackend
from .decryption_backend import DecryptionBackend
from core.context import ctx
from core.module import module_register
from .tools import *

logger = logging.getLogger(__name__)


class DecryptionStream(io.IOBase):
    def __init__(self, stream:VFile):
        super().__init__()
        self.stream = stream
        self._encryptor:DecryptionBackend = None
        self._module = module_register.get('cryptography')

        logger.info(f'initializing decryption stream') 
        self._method = getAlgorithm(self.stream._path)

        match self._method:
            case Algorithm.AES256_GCM:
                self._encryptor = AESDecryptionBackend(self.stream)
            case Algorithm.CHACHA20_POLY1305:
                self._encryptor = ChaCha20Poly1305DecryptionBackend(self.stream)
            case _:
                raise ValueError(f'unsupported decryption method: {self._method}')

    def readable(self): return True
    def flush(self): self.stream.flush()
