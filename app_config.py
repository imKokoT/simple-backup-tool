import os
import yaml
import logger
from miscellaneous.get_input import confirm
from properties import *
from miscellaneous.singleton import Singleton 


class Config(metaclass=Singleton):
    def __init__(self):
        # cloud
        self.download_chunk_size = 1024*1024*10 # Google Drive download chunk size; default 10MB 
        self.default_secret = None # default secret, which will used if 'secret' param will not defined at schema  

        # packer
        self.allow_local_replace = True # if true restored backup will rewrite current local changes, if false will create new folder
        self.ask_before_replace = True # if true will ask before replace files
        self.include_gitignore = False # if true will include .gitignore files patterns
        self.ask_for_other_extract_path = True # if true will ask for path if failed to unpack folder
        self.restore_to_tmp_if_path_invalid = False # if true will restore target folder or file to tmp/restored

        # miscellanies
        self.hide_password_len = True
        self.auto_remove_archive = True # if true archives, that was created or downloaded, will be deleted; .tar excluded
        self.human_sizes = False # if true, byte sizes will print in "B", "KB", "MB", "GB", "TB"


    @staticmethod
    def save():
        if not os.path.exists('configs/'):
            os.mkdir('configs')

        with open('configs/config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(Config().__dict__, f)


    @staticmethod
    def load():
        if not os.path.exists('configs/'):
            os.mkdir('configs')
        
        try:
            with open('configs/config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                for k, v in config.items():
                    setattr(Config(), k, v)
                    if k not in Config().__dict__.keys():
                        logger.logger.warning(f'detected unknown parameter "{k}" in config.yaml')
                if config != Config().__dict__:
                    logger.logger.info('updated config.yaml to newer version')
                    Config.save()
        except FileNotFoundError:
            Config.save()
        except yaml.YAMLError as e:
            logger.logger.error(f'failed to load config; {e}')
            if not confirm('do you want to recreate config?'):
                logger.logger.info('process interrupted...')
                exit(0)
            Config.save()


    def onInstanceCreated():
        Config.load()
