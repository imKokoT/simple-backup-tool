import logging
import tarfile
from core.pack import ArchiveBackend
from core.vfs import VFile

logger = logging.getLogger(__name__)


class TarBackend(ArchiveBackend):
    arch:tarfile.TarFile
    def __init__(self, compressFormat:str, compressLevel:int):
        self.compressFormat = compressFormat
        self.compressLevel = compressLevel

    def open(self, path, mode):
        vf = VFile(path, mode)
        match self.compressFormat:
            case 'tar': 
                if self.compressLevel > 0:
                    logger.warning('TAR does not support compress level')
                self.arch = tarfile.open(None, 'w:tar', fileobj=vf)
            case 'gz': self.arch = tarfile.open(None, 'w:gz', fileobj=vf, compresslevel=self.compressLevel)
            case 'xz': self.arch = tarfile.open(None, 'w:xz', fileobj=vf, preset=self.compressLevel) # who is that impressive guy, who didn't standardize compress level
            case 'bz2': self.arch = tarfile.open(None, 'w:bz2', fileobj=vf, compresslevel=self.compressLevel)
            case 'zst': self.arch = tarfile.open(None, 'w:zst', fileobj=vf, level=self.compressLevel)
        
    def close(self):
        self.arch.close()
    
    def add_file(self, src, dst):
        self.arch.add(src, dst)
    
    def add_bytes(self, data, dst):
        meta = tarfile.TarInfo(dst)
        meta.size = data.getbuffer().nbytes
        self.arch.addfile(meta, fileobj=data)
