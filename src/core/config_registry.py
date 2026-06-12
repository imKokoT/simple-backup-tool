from dataclasses import dataclass
import logging
from typing import TypeVar, Union, get_origin, get_args, Any, Callable, Type

logger = logging.getLogger(__name__)
T = TypeVar('T')


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


@dataclass(init=False)
class ConfigKeyDescription:
    """
    Dynamic ConfigKey description, that could be useful, for instance, when register
    configs with mutable validation
    
    Example:
    ```python
    mutableVariant = ['a', 'b', 'c']

    d = D('possible values: {variant}',
          variant=lambda: ', '.join(mutableVariant))

    print(d)  # possible values: a, b, c

    mutableVariant += ['d', 'e']

    print(d)  # possible values: a, b, c, d, e
    ```
    """
    def __init__(self, raw:str, **kwargs:Callable[[], str]):
        self.raw = raw
        self.kwargs = kwargs

    def __str__(self):
        out = {k: v() for k, v in self.kwargs.items()}
        return self.raw.format(**out)

# shortcut
D = ConfigKeyDescription


@dataclass(slots=True)
class ConfigKey:
    """Describes key of some setting"""
    _registry:'ConfigRegistry'

    name:str
    type:type[T]
    default:Any
    description:D | str = ""
    validator:Callable[[T], bool] | None = None
    required:bool = False

    def validate(self, value: Any):
        if not isinstance_generic(value, self.type):
            logger.error(f'ConfigKey "{self.name}" from "{self._registry.name}" excepts type {self.type}')
            quit(1)
        if self.validator and not self.validator(value):
            logger.error(f'ConfigKey "{self.name}" from "{self._registry.name}" is invalid')
            quit(1)


class ConfigRegistry:
    """Saves all ConfigKeys"""
    def __init__(self, name:str):
        self.name = name
        self._keys: dict[str, ConfigKey] = {}

    def __getitem__(self, key:str) -> ConfigKey:
        return self._keys[key]

    def register(
        self,
        name:str,
        type:type[T],
        default:Any,
        description:ConfigKeyDescription | str = "",
        validator:Callable[[T], bool] | None = None,
        required:bool = False
    ):
        """Register ConfigKey to registry"""
        if name in self._keys:
            raise KeyError(f'ConfigKey "{name}" already registered')

        self._keys[name] = ConfigKey(
            self,
            name=name,
            type=type,
            default=default,
            description=description,
            validator=validator,
            required=required
        )
        logger.debug(f'registered "{name}" ConfigKey in registry "{self.name}"')

    def isRegistered(self, key:str):
        if key not in self._keys:
            raise RuntimeError(f'ConfigKey "{key}" not registered')

    def get(self, key:str) -> ConfigKey:
        return self._keys[key]

    def all(self):
        return self._keys.values()
    
    def keys(self):
        return self._keys.keys()
