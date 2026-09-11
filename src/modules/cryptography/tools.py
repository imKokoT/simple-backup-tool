from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

from core.vfs import VFile

VERSION = b'\x01'
MAGIC = b'EPCK'
SALT = 16


class WrongPasswordError(Exception): ...


class Algorithm(IntEnum):
    AES256_GCM = 1
    CHACHA20_POLY1305 = 2
    # XCHACHA20_POLY1305 = 3


@dataclass(init=False)
class Header:
    magic = MAGIC
    version:int
    algorithm:Algorithm
    salt:bytes
    nonce:bytes


def isEncrypted(packStream:VFile):
    '''returns True if MAGIC is encrypted package'''
    last = packStream.tell()
    packStream.seek(0)

    magic = packStream.read(4)

    packStream.seek(last)
    return magic == MAGIC


def getAlgorithm(packStream:VFile) -> Algorithm:
    '''Returns Algorithm, that used in EPCK'''
    last = packStream.tell()
    packStream.seek(5)

    algorithm = Algorithm.from_bytes(packStream.read(1))

    packStream.seek(last)
    return algorithm
