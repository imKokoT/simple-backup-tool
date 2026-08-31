from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

VERSION = b'\x01'
MAGIC = b'EPKG'
SALT = 16


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


def isEncrypted(packPath:Path):
    '''returns True if MAGIC is encrypted package'''
    with packPath.open('rb') as pk:
        magic = pk.read(4)
    return magic == MAGIC
