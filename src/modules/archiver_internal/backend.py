import logging
import shutil
import tarfile

from core.context import ctx
from core.pack import ArchiveBackend

logger = logging.getLogger(__name__)


class TarBackend(ArchiveBackend):
    arch:tarfile.TarFile
    BACKEND_ID = b'internal'
    
    def __init__(self, stream):
        super().__init__(stream)
        schema = ctx.schema
        self.compressFormat:str = schema.get('packer.format')
        self.compressLevel:int = schema.get('packer.level')

    def set_backend_args(self):
        self.backend_args = bytes(16)
    
    def read_backend_args(self, header):
        ...

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

    def read_file_bytes(self, src):
        member = self.arch.getmember(src)
        return self.arch.extractfile(member)
    
    def restore_file(self, src, dst):
        member = self.arch.getmember(src)
        with self.arch.extractfile(member) as ext: # type: ignore
            with open(dst, 'wb') as f:
                shutil.copyfileobj(ext, f, 1024*1024)
    