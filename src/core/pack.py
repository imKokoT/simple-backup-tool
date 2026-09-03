import io
import json
import logging
import os
import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from core.vfs import VFile

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.schema import Schema

logger = logging.getLogger(__name__)

MAGIC = b'SBTP'
VERSION = 1
HEADER_FORMAT = '<4sB32s16s64s'


class ArchiveBackend(ABC):
    stream:VFile         # stream object where the backend writes archive
    backend_args:bytes   # helper args to manage archive; MAX 16 bytes
    BACKEND_ID:bytes     # important to detect what backed to use to open archive; MAX 32 bytes

    def __init__(self, stream:VFile):
        self.stream = stream

    @abstractmethod
    def set_backend_args(self):
        '''set args that will be written to the pack header while backend is initializing'''
    
    @abstractmethod
    def read_backend_args(self, header:bytes):
        '''read args from provided header'''

    @abstractmethod
    def add_file(self, src:Path, dst:str):
        '''add a file to the archive from path'''
    
    @abstractmethod
    def add_bytes(self, data:io.BytesIO, dst:str):
        '''add a file to archive from bytes'''

    @abstractmethod
    def read_file_bytes(self, src:Path) -> io.BytesIO:
        '''read a file from archive to bytes'''

    @abstractmethod
    def restore_file(self, src:Path, dst:str):
        '''restore a file from archive to a disk'''

    @abstractmethod
    def open(self, mode:Literal['r', 'w']): ...

    @abstractmethod
    def close(self): ...


@dataclass(init=False)
class PackConfig:
    createdAt:str
    schema:Schema
    targetFolders:list[str]
    targetFiles:list[str]
    foldersFiles:list[list[str]]

    def get(self) -> dict:
        return {
            'created_at': self.createdAt,
            'schema': {
                'name': self.schema.name,
                'path': str(self.schema.path),
                'values': self.schema._values
            },
            'folders': self.targetFolders,
            'files': self.targetFiles
        }
    
    def fromDict(self, d:dict):
        raise NotImplementedError()


class Pack:
    """Interface to manage a pack"""
    _configured = False
    _packed = False
    _backend:ArchiveBackend
    _header:bytes

    def __init__(self, mode:Literal['r', 'w'], packStream:VFile):
        self.mode = mode
        self._stream = packStream

        logger.debug(f'open pack {mode=}')
        if mode == 'w':
            ...
        elif mode == 'r':
            self._header = self._stream.read(struct.calcsize(HEADER_FORMAT))
        else:
            raise ValueError(f'unknown backend mode {mode}')

    # --- GENERAL -------------------------------------------------------

    def open(self, backend:ArchiveBackend, **kwargs):
        '''open pack with backend'''
        self._backend = backend
        if self.mode == 'w':
            backend.set_backend_args()
            self._header = struct.pack(
                HEADER_FORMAT,
                MAGIC,
                VERSION,
                backend.BACKEND_ID,
                backend.backend_args,
                kwargs.get('reserved', bytes(64)) # reserved space
            )
            self._stream.write(self._header)
        elif self.mode == 'r':
            backend.read_backend_args(self._header)
            self._packed = True
            self._configured = True

        logger.debug(f'open archive within backend')
        self._backend.open(self.mode)
    
    def close(self):
        if self.mode == 'w' and not self._configured:
            raise RuntimeError(f'tried to close uncofigured pack "{self.path}"')
        if self.mode == 'w' and not self._packed:
            raise RuntimeError(f'tried to close pack without packing data"{self.path}"')
        
        self._backend.close()
        logger.debug(f'closed pack')

    def getBackendId(self) -> str:
        '''returns backend id from pack's header'''
        if not self._header:
            raise AttributeError('pack must be opened within backend')
        return struct.unpack(HEADER_FORMAT, self._header)[2].decode('utf-8').replace('\x00', '')

    # --- READ MODE -----------------------------------------------------
    
    def readConfig(self) -> PackConfig:
        s = self._backend.read_file_bytes('config')
        jsonData = s.read().decode()
        pc = PackConfig()
        pc.fromDict(json.loads(jsonData))
        return pc
    
    def read_file_bytes(self, src:Path) -> io.BytesIO:
        return self._backend.read_file_bytes(src)

    def restore_file(self, src:Path, dst:str):
        self._backend.restore_file(src, dst)

    # --- WRITE MODE ----------------------------------------------------

    def dumpConfig(self, config:PackConfig):
        '''Finalize pack; must be called after data is packed'''
        jsonData = json.dumps(config.get(), indent=1)
        jsonData = io.BytesIO(jsonData.encode())
        self._backend.add_bytes(jsonData, 'config')
        self._configured = True

    def add_file(self, src:Path, dst:str):
        if not os.path.exists(src):
            logger.error(f'failed to pack file {src} because it not exists')
            return
        self._backend.add_file(src, dst)

    def add_bytes(self, data:bytes, dst:str):
        self._backend.add_bytes(data, dst)

    def pack_data(self, config:PackConfig):
        '''Pack folders and files from PackConfig; must be called after the pack is opened'''
        # add files
        logger.info('adding target files...')
        for i, f in enumerate(config.targetFiles):
            self.add_file(f, f'files/{hex(i)[2:]}')

        # add folders
        for i, (tf, files) in enumerate(zip(config.targetFolders, config.foldersFiles)):
            logger.info(f'adding target folder {tf}')
            for file in files:
                self.add_file(f'{tf}/{file}', f'folders/{hex(i)[2:]}/{file}')
        
        self._packed = True
