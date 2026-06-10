import io
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.schema import Schema

logger = logging.getLogger(__name__)


class ArchiveBackend(ABC):
    @abstractmethod
    def add_file(self, src:Path, dst:str):
        '''add a file to the archive from path'''
    
    @abstractmethod
    def add_bytes(self, data:io.BytesIO, dst:str):
        '''add a file to archive from bytes'''

    @abstractmethod
    def open(self, path:Path, mode:Literal['r', 'w']): ...

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
    def __init__(self, backend:ArchiveBackend, path:Path, mode:Literal['r', 'w']):
        self._backend = backend
        self.path = path
        self.packConfig = PackConfig()

        logger.debug(f'open pack "{path}"')
        self._backend.open(path, mode)

    def dumpConfig(self):
        jsonData = json.dumps(self.packConfig.get(), indent=1)
        jsonData = io.BytesIO(jsonData.encode())
        self._backend.add_bytes(jsonData, 'config')

    def readConfig(self):
        raise NotImplementedError()

    def add_file(self, src:Path, dst:str):
        self._backend.add_file(src, dst)

    def add_bytes(self, data:bytes, dst:str):
        self._backend.add_bytes(data, dst)

    def close(self):
        self._backend.close()
        logger.debug(f'closed pack "{self.path}"')
