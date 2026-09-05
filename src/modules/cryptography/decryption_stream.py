import io
import logging

from core.vfs import VFile
from .backends.chacha20_poly1305 import ChaCha20Poly1305DecryptionBackend
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

        self._method = getAlgorithm(self.stream._path)

        match self._method:
            case Algorithm.AES256_GCM:
                logger.info(f'initializing decryption stream; method: AES')
                self._encryptor = AESDecryptionBackend(self.stream)
            case Algorithm.CHACHA20_POLY1305:
                logger.info(f'initializing decryption stream; method: CHACHA20_POLY1305')
                self._encryptor = ChaCha20Poly1305DecryptionBackend(self.stream)
            case _:
                raise ValueError(f'unsupported decryption method')
    
    def read(self, n:int = -1) -> bytes:
        return self._encryptor.read(n)
    
    def seek(self, offset:int, whence:int = 0) -> int: 
        return self._encryptor.seek(offset, whence)
    
    def readable(self): return True
    def flush(self): self.stream.flush()
    def tell(self) -> int: return self._encryptor.tell()
