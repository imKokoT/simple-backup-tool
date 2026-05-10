from abc import ABC, abstractmethod
from argparse import ArgumentParser
from contextlib import contextmanager
from core.context import ctx
from core.schema import schema_config_registry
import logging

logger = logging.getLogger(__name__)


@contextmanager
def _setCurrent(module):
    old = ctx.currentModule
    ctx.currentModule = module

    try:
        yield
    finally:
        ctx.currentModule = old


class Module(ABC):
    schema_config_registry = schema_config_registry

    name:str
    description:str
    schemaParams:list[str] = [] # registered Schema params
    chainArgs:list[str] = []    # defined Chain's command arguments

    def __init__(self, argParser:ArgumentParser):
        self.parser:ArgumentParser = argParser
        self.argGroup = self.parser.add_argument_group(self.name)

    @abstractmethod
    def registerCommandArguments(self):
        """register additional options provided by module for CLI"""

    @abstractmethod
    def registerSchemaParams(self):
        """register Module's schema parameters"""

    @abstractmethod
    def entry(self):
        """
        Module's body logic

        It is good idea to leave entry as simpler as possible
        Example:
        ```python
        from core.module import Module
        from .body import entry # Module-scope module with `entry()` func

        class ExampleModule(Module):
            ...

            def entry(self):
                entry()

            ...
        ``` 
        
        **WARNING**: call `self.invoke()` instead of this to run module logic
        """

    def invoke(self):
        """invoke Module's entry"""
        with _setCurrent(self):
            self._requireChainArguments()
            self.entry()
    
    def _registeredSchemaParams(self): 
        for p in self.schemaParams:
            schema_config_registry.isRegistered(p)

    def _requireChainArguments(self):
        for a in self.chainArgs:
            if a not in ctx.args.__dict__.keys():
                raise KeyError(f'{self} require from Chain command argument "{a}"')


class ModuleRegister:
    def __init__(self):
        self._modules:dict[str, Module] = {}

    def register(self, module:Module):
        logger.debug(f'registering "{module.name}"... ({module})')
        if module.name in self._modules.keys():
            msg = f'Module "{module.name}" already exists!'
            logger.critical(msg)
            raise ValueError(msg)
        
        module._registeredSchemaParams()
        module.registerSchemaParams()
        module.registerCommandArguments()
        self._modules[module.name] = module

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
