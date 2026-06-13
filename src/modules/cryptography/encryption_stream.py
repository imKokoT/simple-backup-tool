import io
import logging

from core.context import ctx
from core.module import module_register
from core.vfs import VFile
from .encryption_backend import EncryptionBackend

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
                self._encryptor = ...
            case _:
                raise ValueError(f'unsupported encryption method: {self._method}')
            
        self._encryptor.writeHeader()

    def write(self, data:bytes) -> int:
        self._encryptor.write(data)
        return len(data)

    def close(self):
        self._encryptor.finalize()
        self.stream.close()

    def writable(self): return True
    def flush(self): self.stream.flush()
