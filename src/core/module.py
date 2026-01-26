from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
import logging

logger = logging.getLogger(__name__)


class Module(ABC):
    name:str
    description:str

    def __init__(self, argParser:ArgumentParser):
        self.parser:ArgumentParser = argParser
        self.argGroup = self.parser.add_argument_group(self.name)

    @abstractmethod
    def requireSchemaParams(self): 
        """define what schema params are required by module"""

    @abstractmethod
    def registerCommandArguments(self):
        """register additional options provided by module for CLI"""

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
        
        module.registerCommandArguments()
        module.requireSchemaParams()
        self._modules[module.name] = module
        
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
    """
    name:str
    description:str
    chian:list[str]
     
    def __init__(self, argParser:ArgumentParser):
        self.parser:ArgumentParser = argParser
        self.subparsers = self.parser.add_subparsers(dest="command", required=True)
        subparser = self.subparsers.add_parser(self.name, help=self.description)
        self.registerCommandArguments()
        subparser.set_defaults(func=self.run)

    @abstractmethod
    def registerCommandArguments(self):
        """register command arguments to run it within CLI"""

    @abstractmethod
    def run(self, args):
        """run chain of modules"""
