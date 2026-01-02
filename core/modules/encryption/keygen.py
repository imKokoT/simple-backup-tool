from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os
from logger import logger

KEY_SIZE = 32
ITERATIONS = 100_000


def keygen(password:str, salt:bytes) -> bytes:
    logger.debug('generating key from password')
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password.encode())


def bytesgen(size:int) -> bytes:
    return os.urandom(size)
