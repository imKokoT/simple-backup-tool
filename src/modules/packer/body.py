import gzip
from io import TextIOWrapper
import json
import logging
from core.cli import humanSize
from core.context import ctx
from core.module import module_register
from core.vfs import VFile, size
from paths import getTmpDir
from properties import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import PackerModule
    from modules.cryptography import CryptographyModule

logger = logging.getLogger(__name__)


def entry():
    module:PackerModule = ctx.currentModule
    schema = ctx.schema
    args = ctx.args
    logger.info('packing files to archive...')

    loadScancache()

    # select module for packing/compressing
    archiver = module_register.get(
        module.archiverModules[
            module.archiverTypes.index(
                schema.get('packer.archiver')
            )]
    )

    # prepare pack stream & invoke archiver 
    module.packStream = s = VFile(module.packPath, 'w')
    if schema.get('encryption'):
        c:CryptographyModule = module_register.get('cryptography')
        s = c.encryptionStream(s)
    archiver.invoke(stream=s, mode='compress')

    logger.info(f'created pack successfully! final size: {humanSize(size(module.packPath))}')


def loadScancache():
    module:PackerModule = ctx.currentModule
    schema = ctx.schema
    logger.debug('preparing PackConfig')

    cachePath = getTmpDir() / schema.name / 'scancache'
    with VFile(cachePath, 'r') as vf:
        if DEBUG:
            with TextIOWrapper(vf, encoding="utf-8") as f:
                data = json.load(f)
        else:
            with gzip.GzipFile(fileobj=vf, mode="rb") as gz:
                with TextIOWrapper(gz, encoding="utf-8") as f:
                    data = json.load(f)

    try:
        module.packConfig.createdAt = data['meta']['session']
        module.packConfig.targetFolders = data['folders']
        module.packConfig.targetFiles = data['files']
        module.packConfig.foldersFiles = data['foldersFiles']
    except KeyError as e:
        logger.error(f'invalid scancache: {e}')
        quit(1)
