from logger import logger
from miscellaneous.singleton import Singleton
from properties import *


class RuntimeData(metaclass=Singleton):
    """
    Saves temporal data in RAM while app runs.

    #### MAIN RUNTIME VARS
     - schema -> loaded backup schema
     - service -> when service was build; service access
    """
    _data:dict = {
        'version': VERSION,
        'debug': DEBUG,
    }

    def push(self, name:str, value, overwrite:bool = False):
        if name in self._data.keys() and not overwrite:
            raise ValueError(f'"{name}" already exists')
        
        logger.debug(f'"{name}" pushed to runtime data')
        self._data[name] = value

    def pop(self, name:str):
        logger.debug(f'from runtime data popped "{name}"')
        return self._data.pop(name)
    
    def tryPop(self, name:str):
        if name in self._data.keys():
            return self.pop(name)
        logger.debug(f'try to pop "{name}" failed')
    
    def __getitem__(self, name:str):
        if name in self._data.keys():
            return self._data[name]
    
    def __setitem__(self, name:str, value):
        self.push(name, value)

# RuntimeData() alias
rtd = RuntimeData()
