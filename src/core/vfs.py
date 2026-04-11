from io import BytesIO, FileIO, IOBase
import os
from pathlib import Path
from typing import Literal
import logging

logger = logging.getLogger(__name__)


class VirtualFS:
    """Virtual filesystem to manage virtual files"""
    _opened:dict[Path, 'VFile'] = {}
    _vfs:dict[Path, BytesIO] = {}

    def get(self, path:Path) -> 'VFile | None':
        """get opened VFile"""
        return self._opened.get(path)
    
    def free(self, path:Path):
        """Free data of the closed in-memory VFile"""
        if path in self._opened:
            raise ValueError(f'VFile "{path}" not closed')
        if path not in self._vfs:
            return
        vf = self._vfs.pop(path)
        vf.close()
        logger.debug(f'freed "{path}"')

    def _onClose(self, vf:'VFile'):
        self._opened.pop(vf._path)
        if vf._location != 'ram':
            vf._raw.close()
        logger.debug(f'closed VFile "{vf._path}"')

    def _onOpen(self, vf:'VFile'):
        if vf._path in self._opened:
            raise FileExistsError(f'virtual file "{vf._path}" already exists')
        
        if vf._location is None: # TODO: add app setting
            vf._location = 'disk'

        if vf._location != 'ram' and vf._path in self._vfs:
            raise RuntimeError(f'cannot open VFile on {vf._location} while it exists in-memory')
        
        if vf._location == 'ram':
            if vf._path not in self._vfs:
                self._vfs[vf._path] = BytesIO()
            vf._raw = self._vfs[vf._path]

            if 'w' in vf._mode:
                vf.truncate()
                vf.seek(0)
        elif vf._location == 'disk':
            vf._raw = FileIO(vf._path, vf._mode)
        else:
            raise ValueError(f'invalid VFile location {vf._location}')
        
        self._opened[vf._path] = vf
        logger.debug(f'opened VFile "{vf._path}" on {vf._location}')
        
vfs = VirtualFS()


class VFile(IOBase):
    """
    Virtual file IO that can be stored in RAM or disk
    
    NOTE: You can create only one VFile per path
    """ 
    def __init__(self, path:Path, mode:str='r', location:Literal['ram', 'disk']|None=None):
        self._path = path
        self._mode = mode
        self._location = location
        self._raw:IOBase

        vfs._onOpen(self)

    def flush(self):                                    self._raw.flush()
    def read(self, n:int = -1) -> bytes:                return self._raw.read(n)
    def readline(self, size = -1)-> bytes:              return self._raw.readline(size)
    def readlines(self, hint = -1) -> list[bytes]:      return self._raw.readlines(hint)
    def seek(self, offset:int, whence:int = 0) -> int:  return self._raw.seek(offset, whence)
    def seekable(self) -> bool:                         return self._raw.seekable() 
    def tell(self) -> int:                              return self._raw.tell()
    def truncate(self, size = None) -> int:             return self._raw.truncate(size)
    def write(self, b:bytes) -> int:                    return self._raw.write(b)
    def writelines(self, lines):                        self._raw.writelines(lines)
    def writable(self)-> bool:                          return self._raw.writable()

    def close(self):
        if not self._raw.closed:
            vfs._onClose(self)

    def __getattr__(self, name):
        return getattr(self._raw, name)

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return super().__exit__(exc_type, exc_val, exc_tb)
