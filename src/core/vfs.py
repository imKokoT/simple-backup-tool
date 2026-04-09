from io import BytesIO, FileIO, IOBase
from pathlib import Path
from typing import Literal
import logging

logger = logging.getLogger(__name__)


class VirtualFS:
    """Virtual filesystem to manage virtual files"""
    _vfs:dict[Path, 'VFile'] = {}

    def get(self, path:Path) -> 'VFile | None':
        return self._vfs.get(path)

    def _onClose(self, path:Path):
        self._vfs.pop(path)
        logger.debug(f'closed VFile "{path}"')

    def _onOpen(self, vfile:'VFile'):
        logger.debug(f'open VFile "{vfile._path}" on {vfile._location}')
        if vfile._path in self._vfs:
            raise FileExistsError(f'virtual file "{vfile._path}" already exists')
        self._vfs[vfile._path] = vfile

vfs = VirtualFS()


class VFile(IOBase):
    """Virtual file IO that can be stored in RAM or disk"""
    def __init__(self, path:Path, mode:str='r', data:bytes=b'', location:Literal['ram', 'disk']|None=None):
        if location is None:
            # TODO app configurations of vfile location
            self._file = FileIO(path, mode)
            if data:
                self._file.write(data)
            self._location = 'disk'
        elif location == 'ram':
            self._file = BytesIO(data)
            self._location = location
        elif location == 'disk':
            self._file = FileIO(path, mode)
            if data:
                self._file.write(data)
            self._location = location
        else:
            raise ValueError(f'Unknown storage location "{location}"')
        
        self._path = path
        self._mode = mode
        
        vfs._onOpen(self)

    def read(self, n:int = -1) -> bytes:                return self._file.read(n)
    def write(self, b:bytes) -> int:                    return self._file.write(b)
    def seek(self, offset:int, whence:int = 0) -> int:  return self._file.seek(offset, whence)
    def tell(self) -> int:                              return self._file.tell()

    def close(self):
        if not self._file.closed:
            self._file.close()
            vfs._onClose(self._path)

    def __getattr__(self, name):
        return getattr(self._file, name)

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return super().__exit__(exc_type, exc_val, exc_tb)
