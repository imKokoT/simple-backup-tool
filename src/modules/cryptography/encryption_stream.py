import io
import logging

from core.context import ctx
from core.module import module_register
from core.vfs import VFile
from .encryption_backend import EncryptionBackend
from .backends.aes import AESEncryptionBackend
from .backends.chacha20_poly1305 import ChaCha20Poly1305EncryptionBackend

logger = logging.getLogger(__name__)


class EncryptionStream(io.IOBase):
    def __init__(self, stream:VFile):
        super().__init__()
        self.stream = stream
        self._encryptor:EncryptionBackend = None
        self._module = module_register.get('cryptography')
        self._method:str = ctx.schema.get('encryption')

        logger.info(f'initializing encryption stream; method: {self._method.upper()}')

        match self._method:
            case 'aes':
                self._encryptor = AESEncryptionBackend(self.stream)
            case 'chacha20poly1305':
                self._encryptor = ChaCha20Poly1305EncryptionBackend(self.stream)
            case _:
                raise ValueError(f'unsupported encryption method: {self._method}')
            
        self._encryptor.writeHeader()

    def write(self, data:bytes) -> int:
        self._encryptor.write(data)
        return len(data)

    def close(self):
        # someone did strange things in cryptography so Rust panics at exit
        # it tries to import this class when Python shuts down
        # maybe this panic is temporal and appears only because the tool
        # exits after cryptography is finished, but any way lets this line
        # here...
        from cryptography.exceptions import AlreadyFinalized

        self._encryptor.finalize()
        self.stream.close()

    def writable(self): return True
    def flush(self): self.stream.flush()
