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

    def get(self, key: str) -> ConfigKey:
        return self._keys[key]

    def all(self):
        return self._keys.values()


configRegistry = ConfigRegistry()


class Config:
    """Load and dump app configs"""
    @staticmethod
    def load():
        ...

    @staticmethod
    def dump():
        ...


def registerBaseSettings():
    """Root application settings"""
    configRegistry.register(
        name='human_sizes',
        type=bool,
        default=False,
        description='If true, byte sizes will print in "B", "KB", "MB", "GB", "TB"'
    )
