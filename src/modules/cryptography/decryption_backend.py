from abc import ABC, abstractmethod
import logging

from .keygen import *
from .tools import *
from core.context import ctx
from core.vfs import VFile

logger = logging.getLogger(__name__)


class DecryptionBackend(ABC):
    def __init__(self, stream:VFile):
        self._stream = stream
        
        self._header = h = Header()
        self.readHeader()

        self._key = keygen(
            ctx.schema.get('password').encode(),
            h.salt
        )

    def readHeader(self):
        '''reads everything excluding NONCE; inherited backend override this method to read nonce too'''
        logger.debug(f'read EPCK header')
        h = self._header
        h.magic = self._stream.read(4)
        h.version = int.from_bytes(self._stream.read(1))
        h.algorithm = Algorithm.from_bytes(self._stream.read(1))
        h.salt = self._stream.read(SALT)

    @abstractmethod
    def read(self, n:int = -1) -> bytes: ...