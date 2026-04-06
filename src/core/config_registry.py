from dataclasses import dataclass
import logging
from typing import Union, get_origin, get_args, Any, Callable, Type

logger = logging.getLogger(__name__)


def isinstance_generic(obj, typ):
    if isinstance(typ, tuple):
        return any(isinstance_generic(obj, t) for t in typ)

    origin = get_origin(typ)
    args = get_args(typ)

    if origin is Union:
        return any(isinstance_generic(obj, t) for t in args)

    if origin is None:
        return isinstance(obj, typ)

    if origin in (list, set, tuple):
        if not isinstance(obj, origin):
            return False
        if args:
            return all(isinstance_generic(item, args[0]) for item in obj)
        return True

    if origin is dict:
        if not isinstance(obj, dict):
            return False
        key_type, val_type = args
        return all(
            isinstance_generic(k, key_type) and
            isinstance_generic(v, val_type)
            for k, v in obj.items()
        )

    return isinstance(obj, origin)


@dataclass(slots=True)
class ConfigKey:
    """Describes key of some setting"""
    name:str
    type:Type
    default:Any
    description:str = ""
    validator:Callable[[Any], bool] | None = None

    def validate(self, value: Any):
        if not isinstance_generic(value, self.type):
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

    def require(self, key:str):
        if key not in self._keys:
            raise RuntimeError(f'ConfigKey "{key}" not registered')

    def get(self, key:str) -> ConfigKey:
        return self._keys[key]

    def all(self):
        return self._keys.values()
    
    def keys(self):
        return self._keys.keys()
