from . import zip_archiver
from . import gz_archiver

try:
    from . import bz2_archiver
except ModuleNotFoundError:
    from config import *
    logger.warning(f'bz2 module not installed!')