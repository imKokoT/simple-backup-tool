import logging
import tarfile
from core.pack import ArchiveBackend

logger = logging.getLogger(__name__)


class TarBackend(ArchiveBackend):
    arch:tarfile.TarFile
    
    def __init__(self, stream, compressFormat:str, compressLevel:int):
        super().__init__(stream)
        self.compressFormat = compressFormat
        self.compressLevel = compressLevel

    def open(self, mode):
        if mode == 'r':
            self.arch = tarfile.open(None, 'r', fileobj=self.stream)
            return

        match self.compressFormat:
            case 'tar': 
                if self.compressLevel > 0:
                    logger.warning('TAR does not support compress level')
                self.arch = tarfile.open(None, 'w:tar', fileobj=self.stream)
            case 'gz': self.arch = tarfile.open(None, 'w:gz', fileobj=self.stream, compresslevel=self.compressLevel)
            case 'xz': self.arch = tarfile.open(None, 'w:xz', fileobj=self.stream, preset=self.compressLevel) # who is that impressive guy, who didn't standardize compress level
            case 'bz2': self.arch = tarfile.open(None, 'w:bz2', fileobj=self.stream, compresslevel=self.compressLevel)
            case 'zst': self.arch = tarfile.open(None, 'w:zst', fileobj=self.stream, level=self.compressLevel)
        
    def close(self):
        self.arch.close()
        self.stream.close()
    
    def add_file(self, src, dst):
        self.arch.add(src, dst)
    
    def add_bytes(self, data, dst):
        meta = tarfile.TarInfo(dst)
        meta.size = data.getbuffer().nbytes
        self.arch.addfile(meta, fileobj=data)
