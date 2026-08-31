import io

from core.vfs import VFile


class DecryptionStream(io.IOBase):
    def __init__(self, stream:VFile):
        super().__init__()
        self.stream = stream
