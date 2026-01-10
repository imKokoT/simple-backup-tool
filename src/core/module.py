from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class Module(ABC):
    name:str

    @abstractmethod
    def registerSchemaParams(self): ...

    @abstractmethod
    def run(self): ...


class ModuleRegister:
    def __init__(self):
        self._modules:dict[str, Module] = {}

    def register(self, module:Module):
        if module.name in self._modules.keys():
            msg = f'Module "{module.name}" already exists!'
            logger.critical(msg)
            raise ValueError(msg)
        module[module.name] = module
        logger.debug(f'registered "{module.name}" ({module})')

    def get(self, name:str) -> Module:
        if name not in self._modules:
            msg = f'Module "{name}" not exists!'
            logger.critical(msg)
            raise KeyError(msg)
        return self._modules[name]

    def all(self):
        return self._modules.values()


register = ModuleRegister()


class Chain(ABC):
    """
    Module chain of some process. Chain defines sequence of process execution.

    Initialization 
    """
    def __init__(self, modules:list[str]=[]):
        self.chian:list[str] = modules

    @abstractmethod
    def registerCommand(self):
        """register command for CLI"""

    def run(self):
        """run chain of modules"""
        for moduleName in self.chian:
            module = register.get(moduleName)
            module.run()
