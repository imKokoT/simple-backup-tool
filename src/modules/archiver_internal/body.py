import logging
from .backend import TarBackend
from core.context import ctx
from core.module import module_register
from core.pack import Pack
from properties import *

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
    module.pack = pack = Pack(
        TarBackend(compressFormat, compressLevel),
        packer.packPath, 
        'w'
    )
    
    pack.pack_data(packConfig)

    pack.dumpConfig(packConfig)
    pack.close()

def decompress():
    raise NotImplementedError()
