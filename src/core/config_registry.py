from dataclasses import dataclass
import logging
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
    def __init__(self, name:str):
        self.name = name
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
        logger.debug(f'registered "{name}" ConfigKey in registry "{self.name}"')

    def get(self, key:str) -> ConfigKey:
        return self._keys[key]

    def all(self):
        return self._keys.values()
    
    def keys(self):
        return self._keys.keys()
