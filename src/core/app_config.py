from paths import *
from properties import *
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.error import YAMLError
import logging
from dataclasses import dataclass
from typing import Any, Callable, Type

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ConfigKey:
    """Describes key of some setting"""
    name:str
    type:Type
    default:Any
    description:str = ""
    validator:Callable[[Any], bool] | None = None

    def validate(self, value: Any):
        if not isinstance(value, self.type):
            raise TypeError(f'{self.name}: expected {self.type.__name__}')
        if self.validator and not self.validator(value):
            raise ValueError(f'{self.name}: validation failed')


class ConfigRegistry:
    """Saves all ConfigKeys"""
    def __init__(self):
        self._keys: dict[str, ConfigKey] = {}

    def __getitem__(self, key:str) -> ConfigKey:
        return self._keys[key]

    def register(
        self,
        name: str,
        *,
        type: type,
        default,
        description: str = "",
        validator=None,
    ):
        """Register ConfigKey to registry"""
        if name in self._keys:
            raise KeyError(f'ConfigKey "{name}" already registered')

        self._keys[name] = ConfigKey(
            name=name,
            type=type,
            default=default,
            description=description,
            validator=validator,
        )
        logger.debug(f'registered "{name}" ConfigKey')

    def get(self, key:str) -> ConfigKey:
        return self._keys[key]

    def all(self):
        return self._keys.values()
    
    def keys(self):
        return self._keys.keys()

configRegistry = ConfigRegistry()


class Config:
    """Load and dump app configs"""
    _values:dict[str, object] = {}
    
    def get(self, key:str):
        if key not in self._values:    
            self._values[key] = configRegistry.get(key).default
        return self._values[key]

    def set(self, name:str, value):
        key = configRegistry.get(name)
        key.validate(value)
        self._values[name] = value

    def load(self):
        path = get_app_dir() / "config.yaml"

        if not path.exists():
            logger.warning("config.yaml not found; dumping default one")
            self.dump()
            return

        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.load(f)
        except YAMLError as e:
            logger.error(f"config.yaml has bad format: {e}")
            raise RuntimeError("Invalid config.yaml") from e

        if not isinstance(data, dict):
            logger.error(f'config.yaml root must be a mapping')
            raise RuntimeError("config.yaml root must be a mapping")

        for k,v in data.items():
            if k not in configRegistry.keys():
                logger.warning(f'unknown config key: {k}')
                continue
            self.set(k, v)

        logger.debug('loaded config.yaml')

        if len(data) != len(configRegistry.all()):
            self.dump()
            logger.info('updated config.yaml to actual version')
        
    def dump(self):
        path = get_app_dir() / "config.yaml"
        path_old = get_app_dir() / "config-old.yaml"
        if path.exists():             
            path.replace(path_old)

        data = CommentedMap()

        for key in configRegistry.all():
            value = self.get(key.name)
            data[key.name] = value

            if key.description:
                # data.yaml_set_comment_before_after_key(
                #     key.name,
                #     before=key.description
                # )
                data.yaml_add_eol_comment(key.description, key.name)

        with path.open("w", encoding="utf-8") as f:
            yaml.dump(data, f)

        logger.debug("dumped config.yaml")

config = Config()


def registerBaseSettings():
    """Root application settings"""
    configRegistry.register(
        name='accessability.human_sizes',
        type=bool,
        default=False,
        description='If true, byte sizes will print in "B", "KB", "MB", "GB", "TB"'
    )
