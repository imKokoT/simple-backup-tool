from io import BytesIO, FileIO, IOBase
from pathlib import Path
from typing import Literal


class VirtualFS:
    """Virtual filesystem to manage virtual files"""
    _vfs:dict[Path, 'VFile'] = {}

    def get(self, path:Path) -> 'VFile | None':
        return self._vfs.get(path)

    def _onClose(self, path:Path):
        self._vfs.pop(path)

    def _onOpen(self, vfile:'VFile'):
        if vfile._path in self._vfs:
            raise FileExistsError(f'virtual file "{vfile._path}" already exists')
        self._vfs[vfile._path] = vfile

vfs = VirtualFS()


class VFile(IOBase):
    """Virtual file IO that can be stored in RAM or disk"""
    def __init__(self, path:Path, mode:str='r', data:bytes=b'', location:Literal['ram', 'disk']|None=None):
        if location is None:
            raise NotImplementedError() # TODO app configurations of location
        elif location == 'ram':
            self._file = BytesIO(data)
        elif location == 'disk':
            self._file = FileIO(path, mode)
            if data:
                self._file.write(data)
        else:
            raise ValueError(f'Unknown storage location "{location}"')
        
        self._path = path
        self._mode = mode
        self._location = location
        
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
