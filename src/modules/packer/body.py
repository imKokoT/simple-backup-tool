import gzip
from io import TextIOWrapper
import json
import logging
from core.context import ctx
from core.vfs import VFile
from paths import getTmpDir
from properties import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import PackerModule

logger = logging.getLogger(__name__)


def entry():
    module:PackerModule = ctx.currentModule
    schema = ctx.schema
    args = ctx.args
    logger.info('packing files to archive...')

    loadScancache()


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
