
try:
    from . import bz2_archiver
except ModuleNotFoundError:
    from logger import logger
    logger.warning(f'bz2 module not installed!')

try:
    from . import gz_archiver
except ModuleNotFoundError:
    from logger import logger
    logger.warning(f'gzip module not installed!')

try:
    from . import zip_archiver
except ModuleNotFoundError:
    from logger import logger
    logger.warning(f'zipfile module not installed!')
    