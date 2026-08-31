import struct

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from ..encryption_backend import EncryptionBackend
from ..tools import *
from ..keygen import *

CHUNK_SIZE = 1024*1024


def make_chunk_nonce(base_nonce, index):
    return (
        base_nonce[:4] +
        index.to_bytes(8, "little")
    )

class AESEncryptionBackend(EncryptionBackend):
    def __init__(self, stream):
        super().__init__(stream)

        h = self._header
        h.algorithm = Algorithm.AES256_GCM
        h.nonce = bytesgen(12)

        self._buffer = bytearray()
        self._chunk_index = 0

    def write(self, data):
        self._buffer.extend(data)

        while len(self._buffer) >= CHUNK_SIZE:
            chunk = bytes(self._buffer[:CHUNK_SIZE])
            del self._buffer[:CHUNK_SIZE]
            self._encrypt_chunk(chunk)

    def _encrypt_chunk(self, data):
        nonce = make_chunk_nonce(self._header.nonce, self._chunk_index)

        encryptor = Cipher(
            algorithms.AES(self._key),
            modes.GCM(nonce)
        ).encryptor()

        # chunk index
        encryptor.authenticate_additional_data(
            struct.pack("<Q", self._chunk_index)
        )

        ciphertext = encryptor.update(data)
        ciphertext += encryptor.finalize()

        self._stream.write(
            struct.pack("<I", len(ciphertext))
        )
        self._stream.write(ciphertext)
        self._stream.write(encryptor.tag)

        self._chunk_index += 1

    def finalize(self):
        if self._buffer:
            self._encrypt_chunk(bytes(self._buffer))
            self._buffer.clear()
