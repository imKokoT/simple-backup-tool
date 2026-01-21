from core.config_registry import ConfigRegistry
from paths import *
from properties import *
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.error import YAMLError
import logging

logger = logging.getLogger(__name__)
app_config_registry = ConfigRegistry('schema_config_registry')


class Schema:
    """Loaded schema file"""
    path:Path
    _values:dict[str, object] = {}
    
    def get(self, key:str):
        if key not in self._values:    
            self._values[key] = app_config_registry.get(key).default
        return self._values[key]

    def set(self, name:str, value):
        key = app_config_registry.get(name)
        key.validate(value)
        self._values[name] = value

    def load(self):
        ...

    def dump(self):
        ...
