import io
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from core.vfs import VFile

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.schema import Schema

logger = logging.getLogger(__name__)


class ArchiveBackend(ABC):
    stream:VFile  # stream object where the backend writes archive

    def __init__(self, stream:VFile):
        self.stream = stream

    @abstractmethod
    def add_file(self, src:Path, dst:str):
        '''add a file to the archive from path'''
    
    @abstractmethod
    def add_bytes(self, data:io.BytesIO, dst:str):
        '''add a file to archive from bytes'''

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
    
    def getMeta(self) -> dict:
        # TODO: return pack metadata
        raise NotImplementedError()


class Pack:
    """Interface to manage a pack"""
    _configured = False
    _packed = False

    def __init__(self, backend:ArchiveBackend, mode:Literal['r', 'w']):
        self._backend = backend
        self.mode = mode

        logger.debug(f'open pack')
        self._backend.open(mode)

    def dumpConfig(self, config:PackConfig):
        '''Finalize pack; must be called after data is packed'''
        jsonData = json.dumps(config.get(), indent=1)
        jsonData = io.BytesIO(jsonData.encode())
        self._backend.add_bytes(jsonData, 'config')
        self._configured = True

    def readConfig(self):
        raise NotImplementedError()

    def add_file(self, src:Path, dst:str):
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

    def close(self):
        if self.mode == 'w' and not self._configured:
            raise RuntimeError(f'tried to close uncofigured pack "{self.path}"')
        if self.mode == 'w' and not self._packed:
            raise RuntimeError(f'tried to close pack without packing data"{self.path}"')
        
        self._backend.close()
        logger.debug(f'closed pack')
