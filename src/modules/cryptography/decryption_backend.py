from abc import ABC, abstractmethod
import logging

from .keygen import *
from .tools import *
from core.context import ctx
from core.vfs import VFile

logger = logging.getLogger(__name__)


class DecryptionBackend(ABC):
    FULL_CHUNK_SIZE:int
    HEADER_LENGTH:int

    def __init__(self, stream:VFile):
        self._stream = stream
        
        self._header = h = Header()
        self.readHeader()

        self._key = keygen(
            ctx.schema.get('password').encode(),
            h.salt
        )

        self._buffer = bytearray()

        # logical position in plaintext
        self._position = 0

    def readHeader(self):
        '''reads everything excluding NONCE; inherited backend override this method to read nonce too'''
        logger.debug(f'read EPCK header')
        h = self._header
        h.magic = self._stream.read(4)
        h.version = int.from_bytes(self._stream.read(1))
        h.algorithm = Algorithm.from_bytes(self._stream.read(1))
        h.salt = self._stream.read(SALT)

    @abstractmethod
    def _read_chunk(self) -> bytes | None: ...

    @abstractmethod
    def read(self, n:int = -1) -> bytes: ...

    @abstractmethod
    def seek(self, offset:int, whence:int = 0) -> int: ...

    def tell(self) -> int:
        return self._position

    def seek(self, offset, whence = 0):
        if whence == 0:
            newPos = offset
        elif whence == 1:
            newPos = self._position + offset
        elif whence == 2:
            raise NotImplementedError('whence 2 not supported')
        else:
            raise ValueError('invalid whence')
        
        if newPos < 0:
            raise ValueError("negative seek position")

        # seek physical pos
        self._stream.seek(self.FULL_CHUNK_SIZE * (newPos // self.FULL_CHUNK_SIZE) + self.HEADER_LENGTH)
        self._chunk_index = newPos // self.FULL_CHUNK_SIZE
        self._buffer.clear()
        self._position = newPos
        self._eof = False

        # decrypt chunk from new physical pos
        chunk = self._read_chunk()
        if chunk is not None:
            self._buffer.extend(chunk[newPos % self.FULL_CHUNK_SIZE:])

        return self._position
    