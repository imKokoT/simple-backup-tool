from io import BytesIO, FileIO, IOBase
import os
from pathlib import Path
from typing import Literal
import logging

from core.app_config import config

logger = logging.getLogger(__name__)


class VirtualFS:
    """Virtual filesystem to manage virtual files"""
    _opened:dict[str, 'VFile'] = {}
    _vfs:dict[str, BytesIO] = {}
    _lastOpenedLocation:dict[str, Literal['r', 'w']] = {}

    def get(self, path:Path) -> 'VFile | None':
        """get opened VFile"""
        return self._opened.get(
           str(os.path.normpath(path))
        )
    
    def free(self, path:Path):
        """Free data of the closed in-memory VFile"""
        path = str(os.path.normpath(path))

        if path in self._opened:
            raise ValueError(f'VFile "{path}" not closed')
        if path not in self._vfs:
            return
        vf = self._vfs.pop(path)
        vf.close()
        logger.debug(f'freed "{path}"')

    def _onClose(self, vf:'VFile'):
        path = str(os.path.normpath(vf._path))

        if path not in self._opened:
            return

        self._opened.pop(path)
        if vf._location != 'ram':
            vf._raw.close()
        else:
            vf._raw.seek(0)
        logger.debug(f'closed VFile "{path}"')

    def _onOpen(self, vf:'VFile'):
        path = str(os.path.normpath(vf._path))

        if path in self._opened:
            raise RuntimeError(f'virtual file "{path}" already opened')
        
        if vf._location is None:
            vf._location = 'ram' if config.get('zero_waste') else 'disk'

        if vf._location != 'ram' and path in self._vfs:
            raise RuntimeError(f'cannot open VFile on {vf._location} while it exists in-memory')
        
        if vf._location == 'ram':
            if path not in self._vfs:
                self._vfs[path] = BytesIO()
            vf._raw = self._vfs[path]

            if 'w' in vf._mode:
                vf.truncate()
                vf.seek(0)
        elif vf._location == 'disk':
            vf._raw = FileIO(path, vf._mode)
        else:
            raise ValueError(f'invalid VFile location {vf._location}')
        
        self._opened[path] = vf
        self._lastOpenedLocation[path] = vf._location
        logger.debug(f'opened VFile "{path}" on {vf._location}')
        
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
    def readable(self):                                 return self._raw.readable()
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


# --- extensions ----------------------------------------------

def exists(path:str|Path) -> bool:
    '''
    returns true if path exists
    
    You must call this function if the file path which you check designed to be managed by VFS
    '''
    path = str(os.path.normpath(path))

    if vfs._lastOpenedLocation.get(path) == 'ram':
        return vfs._vfs.get(path) != None or vfs._opened.get(path)
    else:
        return os.path.exists(path)


def size(path:str|Path) -> int:
    '''
    returns size in bytes
    
    You must call this function if the file path which you check designed to be managed by VFS
    '''
    path = str(os.path.normpath(path))
    
    b = vfs._vfs.get(path)
    if b is not None:
        return b.getbuffer().nbytes
    else:
        return os.stat(path).st_size
