from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import struct

from ..encryption_backend import EncryptionBackend
from ..tools import *
from ..keygen import *

CHUNK_SIZE = 1024 * 256


class ChaCha20Poly1305EncryptionBackend(EncryptionBackend):
    def __init__(self, stream):
        super().__init__(stream)

        h = self._header
        h.nonce = bytesgen(12)
        h.algorithm = Algorithm.CHACHA20_POLY1305

        self._encryptor = ChaCha20Poly1305(self._key)

        self._buffer = bytearray()
        self._chunk_index = 0

    def _chunk_nonce(self, index: int) -> bytes:
        # 12-byte nonce version (ChaCha20-Poly1305 standard)
        # base_nonce[0:8] + counter(4 bytes)
        return (
            self._header.nonce[:8] +
            index.to_bytes(4, "little")
        )
    
    def _write_chunk(self, chunk:bytes):
        nonce = self._chunk_nonce(self._chunk_index)

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

        # end marker
        self._stream.write(struct.pack("<I", 201305))
        self._stream.flush()
