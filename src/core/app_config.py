from core.config_registry import ConfigRegistry
from paths import *
from properties import *
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.error import YAMLError
import logging

logger = logging.getLogger(__name__)
app_config_registry = ConfigRegistry('app_config')


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
            if k not in app_config_registry.keys():
                logger.warning(f'unknown config key: {k}')
                continue
            self.set(k, v)

        logger.debug('loaded config.yaml')

        if len(data) != len(app_config_registry.all()):
            self.dump()
            logger.info('updated config.yaml to actual version')
        
    def dump(self):
        path = get_app_dir() / "config.yaml"
        path_old = get_app_dir() / "config-old.yaml"
        if path.exists():             
            path.replace(path_old)

        data = CommentedMap()

        for key in app_config_registry.all():
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

config = AppConfig()


def registerBaseSettings():
    """Root application settings"""
    app_config_registry.register(
        name='accessability.human_sizes',
        type=bool,
        default=False,
        description='If true, byte sizes will print in "B", "KB", "MB", "GB", "TB"'
    )
