from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import struct

from ..decryption_backend import DecryptionBackend
from ..encryption_backend import EncryptionBackend
from ..tools import *
from ..keygen import *

CHUNK_SIZE = 1024 * 1024
NONCE  = 12
TAG_SIZE = 16


def _chunk_nonce(header:Header, index: int) -> bytes:
    # 12-byte nonce version (ChaCha20-Poly1305 standard)
    # base_nonce[0:8] + counter(4 bytes)
    return (
        header.nonce[:8] +
        index.to_bytes(4, "little")
    )

class ChaCha20Poly1305EncryptionBackend(EncryptionBackend):
    def __init__(self, stream):
        super().__init__(stream)

        h = self._header
        h.nonce = bytesgen(12)
        h.algorithm = Algorithm.CHACHA20_POLY1305

        self._encryptor = ChaCha20Poly1305(self._key)

        self._buffer = bytearray()
        self._chunk_index = 0
    
    def _write_chunk(self, chunk:bytes):
        nonce = _chunk_nonce(self._header, self._chunk_index)

        associated_data = struct.pack("<Q", self._chunk_index)

        encrypted = self._encryptor.encrypt(
            nonce,
            chunk,
            associated_data
        )

        # store length + ciphertext+tag
        self._stream.write(struct.pack("<I", len(encrypted)))
        self._stream.write(encrypted)

        self._chunk_index += 1

    def write(self, data:bytes):
        self._buffer.extend(data)

        while len(self._buffer) >= CHUNK_SIZE:
            chunk = bytes(self._buffer[:CHUNK_SIZE])
            del self._buffer[:CHUNK_SIZE]
            self._write_chunk(chunk)

    def finalize(self):
        if self._buffer:
            self._write_chunk(bytes(self._buffer))
            self._buffer.clear()

        self._stream.flush()


class ChaCha20Poly1305DecryptionBackend(DecryptionBackend):
    def __init__(self, stream):
        super().__init__(stream)

        self._chunk_index = 0
        self._eof = False

        self._decryptor = ChaCha20Poly1305(self._key)

        self.FULL_CHUNK_SIZE = CHUNK_SIZE + TAG_SIZE + 4
        self.HEADER_LENGTH = 34

    def readHeader(self):
        super().readHeader()
        self._header.nonce = self._stream.read(NONCE)

        if len(self._header.nonce) != NONCE:
            raise EOFError("unexpected end of encrypted header")

    def _read_chunk(self) -> bytes | None:
        rawLength = self._stream.read(4)

        if rawLength == b'':
            self._eof = True
            return None
        elif len(rawLength) != 4:
            raise EOFError("unexpected end of encrypted stream")

        length = struct.unpack("<I", rawLength)[0]
        if length < TAG_SIZE:
            raise ValueError("invalid encrypted chunk size")

        encrypted = self._stream.read(length)
        if len(encrypted) != length:
            raise EOFError("incomplete encrypted chunk")

        nonce = _chunk_nonce(self._header, self._chunk_index)

        try:
            plaintext = self._decryptor.decrypt(
                nonce,
                encrypted,
                struct.pack(
                    "<Q",
                    self._chunk_index
                )
            )
        except InvalidTag:
            raise ValueError(
                f"authentication failed for chunk "
                f"{self._chunk_index}"
            ) from None

        self._chunk_index += 1
        return plaintext

    def read(self, size=-1) -> bytes:
        while not self._eof and (size < 0 or len(self._buffer) < size):
            chunk = self._read_chunk()

            if chunk is None:
                break

            self._buffer.extend(chunk)

        if size < 0:
            result = bytes(self._buffer)
            self._buffer.clear()
            self._position += len(result)
            return result

        result = bytes(self._buffer[:size])
        del self._buffer[:size]

        self._position += len(result)

        return result
