from abc import ABC, abstractmethod
from argparse import ArgumentParser
from core.context import ctx
from core.schema import schema_config_registry
import logging

logger = logging.getLogger(__name__)


class Module(ABC):
    name:str
    description:str
    schemaParams:list[str] = []
    chainArgs:list[str] = []

    def __init__(self, argParser:ArgumentParser):
        self.parser:ArgumentParser = argParser
        self.argGroup = self.parser.add_argument_group(self.name)


    @abstractmethod
    def registerCommandArguments(self):
        """register additional options provided by module for CLI"""

    def run(self):
        """run module code. must be overridden with <code>super().run()</code> in the body"""
        ctx.currentModule = self
        self._requireChainArguments()
    
    def _requireSchemaParams(self): 
        for p in self.schemaParams:
            schema_config_registry.require(p)

    def _requireChainArguments(self):
        for a in self.chainArgs:
            if a not in ctx.args.__dict__.keys():
                raise KeyError(f'{self} require from Chain command argument "{a}"')


class ModuleRegister:
    def __init__(self):
        self._modules:dict[str, Module] = {}

    def register(self, module:Module):
        if module.name in self._modules.keys():
            msg = f'Module "{module.name}" already exists!'
            logger.critical(msg)
            raise ValueError(msg)
        
        module._requireSchemaParams()
        module.registerCommandArguments()
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
        self.subparser = self.subparsers.add_parser(self.name, help=self.description)
        self.registerCommandArguments()
        self.subparser.set_defaults(func=self.run)

    @abstractmethod
    def registerCommandArguments(self):
        """register command arguments to run it within CLI"""

    @abstractmethod
    def run(self, args):
        """run chain of modules"""
