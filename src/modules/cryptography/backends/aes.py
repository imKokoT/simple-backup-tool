from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from ..encryption_backend import EncryptionBackend
from ..tools import *
from ..keygen import *


class AESEncryptionBackend(EncryptionBackend):
    def __init__(self, stream):
        super().__init__(stream)

        h = self._header
        h.nonce = bytesgen(12)
        h.algorithm = Algorithm.AES256_GCM
        
        self._encryptor = Cipher(
            algorithms.AES(self._key),
            modes.GCM(h.nonce)
        ).encryptor()

    def write(self, data):
        encrypted = self._encryptor.update(data)
        self._stream.write(encrypted)

    def finalize(self):
        encrypted = self._encryptor.finalize()
        if encrypted:
            self._stream.write(encrypted)

        self._stream.write(self._encryptor.tag)
