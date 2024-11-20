from . import zip_archiver
from . import gz_archiver

try:
    from . import bz2_archiver
except ModuleNotFoundError:
    from logger import logger
    logger.warning(f'bz2 module not installed!')
    