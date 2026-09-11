from core.config_registry import ConfigRegistry
from paths import *
from properties import *
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.error import YAMLError
import logging

logger = logging.getLogger(__name__)
app_config_registry = ConfigRegistry('app_config_registry')


class AppConfig:
    """Load and dump app configs"""
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
        path = getAppDir() / "config.yaml"

        if not path.exists():
            logger.warning("config.yaml not found; dumping default one")
            self.dump()
            return

        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.load(f)
        except YAMLError as e:
            logger.error(f"config.yaml has bad format: {e}")
            quit(1)

        if not isinstance(data, dict):
            logger.error(f'config.yaml root must be a mapping')
            quit(1)

        for k,v in data.items():
            if k not in app_config_registry.keys():
                logger.warning(f'unknown config key: {k}')
                continue
            self.set(k, v)

        logger.debug('loaded config.yaml')

        if data.keys() != app_config_registry.keys():
            self.dump()
            logger.info('updated config.yaml to actual version')
        
    def dump(self):
        path = getAppDir() / "config.yaml"
        path_old = getAppDir() / "config-old.yaml"
        if path.exists():             
            path.replace(path_old)

        data = CommentedMap()

        for key in app_config_registry.all():
            value = self.get(key.name)
            data[key.name] = value

            if key.description:
                if '\n' in key.description:
                    data.yaml_set_comment_before_after_key(
                        key.name,
                        before=f'\n{key.description}'
                    )
                else:
                    data.yaml_add_eol_comment(key.description, key.name)

        with path.open("w", encoding="utf-8") as f:
            yaml.dump(data, f)

        logger.debug("dumped config.yaml")

    def override(self, params:dict):
        logger.debug('overriding app config params')
        for k,v in params.items():
            if k not in app_config_registry.keys():
                continue

            self.set(k, v)

config = AppConfig()


def registerBaseSettings():
    """Root application settings"""
    app_config_registry.register(
        name='appearance.human_sizes',
        type=bool,
        default=False,
        description='If true, byte sizes will print in "B", "KB", "MB", "GB", "TB"'
    )
    app_config_registry.register(
        name='zero_waste',
        type=bool,
        default=False,
        description='If true, all VFiles without specified storage location will be saved to RAM\n' \
                    '\n' \
                    'This feature usually preferred for small and frequent backups (daily or even hourly) to\n' \
                    'increase packing speed and reduce host\'s disk wear while sacrificing some stability\n'
                    '\n'
                    'WARNING: REQUIRES A HUGE AMOUNT OF RAM! Large backups/restores could cause freezes, crashes,\n' \
                    'system slowdown etc, if the system does not have enough RAM.',
    )
