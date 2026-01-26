from typing import Set
from core.config_registry import ConfigRegistry
from paths import *
from properties import *
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.error import YAMLError
import logging

logger = logging.getLogger(__name__)
schema_config_registry = ConfigRegistry('schema_config_registry')


class Schema:
    """Loaded schema file"""
    name:str
    path:Path
    _values:dict[str, object] = {}

    def __init__(self, path:Path):
        self.path = path
        self.name = path.stem
        self.load()
    
    def get(self, key:str):
        if key not in self._values:    
            self._values[key] = schema_config_registry.get(key).default
        return self._values[key]

    def set(self, name:str, value):
        key = schema_config_registry.get(name)
        key.validate(value)
        self._values[name] = value

    def load(self):
        self._loadFile(self.path, visited=set())

    def _loadFile(self, path:Path, visited:Set[Path]):
        logger.debug(f'loading schema "{path}"')

        path = path.resolve()
        if path in visited:
            raise RuntimeError(f'include cycle detected: {path}')
        visited.add(path)

        if not path.exists():
            raise FileNotFoundError(path)

        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.load(f)
        except YAMLError as e:
            raise RuntimeError(f"invalid schema: {path}") from e

        if not isinstance(data, dict):
            raise RuntimeError(f"schema root must be a mapping: {path}")

        # include
        includes = data.get("include", [])
        if isinstance(includes, str):
            includes = [includes]

        for name in includes:
            include_path = (getAppDir() / "schemas" / f"{name}.yaml")
            self._loadFile(include_path, visited)

        # apply overrides
        for k, v in data.items():
            if k == "include": continue
            if k not in schema_config_registry.keys():
                logger.warning(f'unknown schema config key "{k}" in {path}')
                continue
            self.set(k, v)

    def dump(self):
        raise NotImplementedError()


def registerBaseSettings():
    """build-in schemas parameters"""
    schema_config_registry.register(
        name='include',
        type=(list[str], str, type(None)),
        default=None,
        description='Include other schema params from config directory; requires schema\'s name'
    )
    schema_config_registry.register(
        name='targets',
        type=(list[str],),
        default=None,
        description='Target folders and files in local disk to backup'
    )
    schema_config_registry.register(
        name='ignore',
        type=(str, list[str]),
        default='',
        description='Global ignore pattern; highest priority'
    )
