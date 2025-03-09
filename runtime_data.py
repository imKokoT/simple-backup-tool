from logger import logger
from miscellaneous import Singleton


class RuntimeData(metaclass=Singleton):
    _data:dict = {}

    def push(self, name:str, value, overwrite:bool = False):
        if name in self._data.keys() and not overwrite:
            raise ValueError(f'"{name}" already exists')
        
        logger.debug(f'"{name}" pushed to runtime data')
        self._data[name] = value

    def pop(self, name:str):
        logger.debug(f'from runtime data popped "{name}"')
        return self._data.pop(name)
    
    def __getitem__(self, name:str):
        if name in self._data.keys():
            return self._data[name]
    
    def __setitem__(self, name:str, value):
        self.push(name, value)

rtd = RuntimeData()
