from logger import logger
from miscellaneous import Singleton


class RuntimeData(metaclass=Singleton):
    _data:dict = {}

    def set(self, name:str, value):
        self._data[name] = value

    def pop(self, name:str):
        return self._data.pop(name)
    
    def __getitem__(self, name:str):
        if name in self._data.keys():
            return self._data[name]
    
    def __setitem__(self, name:str, value):
        self.set(name, value)

rt = RuntimeData()
