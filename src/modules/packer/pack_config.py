from dataclasses import dataclass

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.schema import Schema


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
