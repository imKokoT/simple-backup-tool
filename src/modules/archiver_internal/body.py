import logging
import tarfile
from core.context import ctx
from core.module import module_register
from core.vfs import VFile
from paths import getTmpDir

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import ArchiverInternalModule
    from modules.packer import PackerModule 

logger = logging.getLogger(__name__)


def entry():
    module:ArchiverInternalModule = ctx.currentModule
    schema = ctx.schema
    args = ctx.args

    if module.invokeArgs['mode'] == 'compress':
        compress()
    elif module.invokeArgs['mode'] == 'decompress':
        decompress()


def compress():
    module:ArchiverInternalModule = ctx.currentModule
    packer:PackerModule = module_register.get('packer')
    schema = ctx.schema

    packConfig = packer.packConfig
    compressFormat:str = schema.get('packer.format')
    compressLevel:int = schema.get('packer.level')

    if compressFormat not in module.supportedFormats:
        logger.error(f'{module.name} does not support format {compressFormat}; '
                    f'supported formats: {', '.join(module.supportedFormats)}')
        quit(1)

    # open archive
    logger.info(f'open {compressFormat.upper()} archive with {module.name}')
    vf = VFile(packer.packPath, 'w')
    match compressFormat:
        case 'tar': 
            if compressLevel > 0:
                logger.warning('TAR does not support compress level')
            module.pack = tarfile.open(None, 'w:tar', fileobj=vf)
        case 'gz': module.pack = tarfile.open(None, 'w:gz', fileobj=vf, compresslevel=compressLevel)
        case 'xz': module.pack = tarfile.open(None, 'w:xz', fileobj=vf, preset=compressLevel) # who is that impressive guy, who didn't standardize compress level
        case 'bz2': module.pack = tarfile.open(None, 'w:bz2', fileobj=vf, compresslevel=compressLevel)
        case 'zst': module.pack = tarfile.open(packer.packPath, 'w:zst', level=compressLevel)
        
    # add folders and files

    module.pack.close()

def decompress():
    raise NotImplementedError()
