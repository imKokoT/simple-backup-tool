from abc import ABC, abstractmethod
import logging

from .keygen import *
from .tools import *
from core.context import ctx
from core.vfs import VFile

logger = logging.getLogger(__name__)


class EncryptionBackend(ABC):
    def __init__(self, stream:VFile):
        self._stream = stream
        
        self._header = h = Header()
        h.version = int.from_bytes(VERSION)
        h.salt = bytesgen(SALT)

        self._key = keygen(
            ctx.schema.get('password').encode(),
            h.salt
        )

    def writeHeader(self):
        h = self._header
        s = self._stream.write(h.magic)
        s += self._stream.write(VERSION)
        s += self._stream.write(h.algorithm.to_bytes())
        s += self._stream.write(h.salt)
        s += self._stream.write(h.nonce)
        logger.debug(f'wrote {s} byte(s) EPKG header V{int.from_bytes(VERSION)}')
        
    @abstractmethod
    def write(self, data:bytes): ...

    @abstractmethod
    def finalize(self): ...
