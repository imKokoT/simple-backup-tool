import struct
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from ..decryption_backend import DecryptionBackend
from ..encryption_backend import EncryptionBackend
from ..tools import *
from ..keygen import *

CHUNK_SIZE = 1024*1024
NONCE = 12
TAG_SIZE = 16
END_MARKER = 0xffffffff
FULL_CHUNK_SIZE = CHUNK_SIZE + TAG_SIZE + 4
HEADER_LENGTH = 34


def _chunk_nonce(base_nonce, index):
    return (
        base_nonce[:4] +
        index.to_bytes(8, "little")
    )

class AESEncryptionBackend(EncryptionBackend):
    def __init__(self, stream):
        super().__init__(stream)

        h = self._header
        h.algorithm = Algorithm.AES256_GCM
        h.nonce = bytesgen(NONCE)

        self._buffer = bytearray()
        self._chunk_index = 0

    def write(self, data):
        self._buffer.extend(data)

        while len(self._buffer) >= CHUNK_SIZE:
            chunk = bytes(self._buffer[:CHUNK_SIZE])
            del self._buffer[:CHUNK_SIZE]
            self._encrypt_chunk(chunk)

    def _encrypt_chunk(self, data):
        nonce = _chunk_nonce(self._header.nonce, self._chunk_index)

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
            struct.pack("<I", len(ciphertext) + TAG_SIZE)
        )
        self._stream.write(ciphertext)
        self._stream.write(encryptor.tag)

        self._chunk_index += 1

    def finalize(self):
        if self._buffer:
            self._encrypt_chunk(bytes(self._buffer))
            self._buffer.clear()


class AESDecryptionBackend(DecryptionBackend):
    def __init__(self, stream):
        super().__init__(stream)

        self._chunk_index = 0
        self._buffer = bytearray()
        self._eof = False

    def readHeader(self):
        super().readHeader()
        h = self._header
        h.nonce = self._stream.read(NONCE)

    def _read_chunk(self) -> bytes | None:
        length_data = self._stream.read(4)

        if len(length_data) != 4:
            raise EOFError("unexpected end of encrypted stream")

        length = struct.unpack("<I", length_data)[0]

        if length == END_MARKER:
            self._eof = True
            return None

        if length < TAG_SIZE:
            raise ValueError("invalid encrypted chunk size")

        encrypted = self._stream.read(length)

        if len(encrypted) != length:
            raise EOFError("incomplete encrypted chunk")

        ciphertext = encrypted[:-TAG_SIZE]
        tag = encrypted[-TAG_SIZE:]

        nonce = _chunk_nonce(self._header.nonce, self._chunk_index)

        decryptor = Cipher(
            algorithms.AES(self._key),
            modes.GCM(nonce, tag)
        ).decryptor()

        associated_data = struct.pack(
            "<Q",
            self._chunk_index
        )

        decryptor.authenticate_additional_data(
            associated_data
        )

        try:
            plaintext = decryptor.update(ciphertext)
            plaintext += decryptor.finalize()
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
            self._position += len(result)
            self._buffer.clear()
            return result

        result = bytes(self._buffer[:size])
        self._position += len(result)
        del self._buffer[:size]

        return result

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
        self._stream.seek(FULL_CHUNK_SIZE * (newPos // FULL_CHUNK_SIZE) + HEADER_LENGTH)
        self._chunk_index = newPos // FULL_CHUNK_SIZE
        self._buffer.clear()
        self._position = newPos
        self._eof = False

        # decrypt chunk from new  physical pos
        chunk = self._read_chunk()
        if chunk is not None:
            self._buffer.extend(chunk[newPos % FULL_CHUNK_SIZE:])

        return self._position
