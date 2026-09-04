import logging
import os
from pathlib import Path

from core.app_config import config
from core.cli import getConfirm
from core.context import ctx
from core.module import module_register
from core.pack import Pack
from core.vfs import VFile
from properties import *

from typing import TYPE_CHECKING

from paths import canCreate, isValid
if TYPE_CHECKING:
    from . import UnpackerModule
    from modules.cryptography import CryptographyModule

logger = logging.getLogger(__name__)


def entry():
    module:UnpackerModule = ctx.currentModule
    schema = ctx.schema
    args  = ctx.args

    logger.info('unpacking loaded pack...')
    module.packStream = s = VFile(module.packPath, 'r')

    # try decrypt pack
    c:CryptographyModule = module_register.get('cryptography')
    if c.isEncrypted(module.packPath):
        logger.info('encryption detected')
        s = c.decryptionStream(s)
    
    # select module for decompressing
    module.pack = Pack('r', s)
    bid = module.pack.getBackendId()

    archiver = module_register.get(
        module.archiverModules[module.archiverType.index(bid)]
    )
    archiver.invoke(stream=s, mode='setup-decompress')

    # ask for replace
    if getConfirm('n', f'Are you sure to rewrite next folders and files:\n'
                       f'{'\n'.join([f' - {f}' for f in module.packConfig.targetFolders])}\t[FOLDER]\n'
                       f'{'\n'.join([f' - {f}' for f in module.packConfig.targetFiles])}\t[FILE]\n'):
        if getConfirm('y', f'Do you want to restore data into {module.restoredFolder}'):
            raise NotImplementedError()
        else:
            exit(0)

    unpack_files()
    unpack_folders()

    module.pack.close()


def unpack_files():
    module:UnpackerModule = ctx.currentModule

    for tf in module.packConfig.targetFiles:
        path = Path(tf)

        # select where to restore
        if not path.parent.exists():
            if config.get('restore.restore_to_restored_if_path_invalid'):
                path = module.restoredFolder / path.name
            else:
                # ask user where to restore file
                path = askAnotherPath(path)
                if not path:
                    logger.info(f'skip file {path}')
                    continue
        else:
            path = path if config.get('restore.allow_local_replace') else path.with_name(f"{path.stem}-restored{path.suffix}")

        module.pack.restore_file(module.packConfig, tf, path)
        logger.info(f'restored file "{tf}" to {path}')


def unpack_folders():
    module:UnpackerModule = ctx.currentModule


def askAnotherPath(path:Path) -> Path:
    module:UnpackerModule = ctx.currentModule
    newPath = path

    if getConfirm('y', f'Target path {path} is invalid; do you want to restore it into "{module.restoredFolder}"'):
        newPath = module.restoredFolder / path.name
    elif getConfirm('n', f'Do you want to restore it into another path'):
        return

    print('Input new valid path')
    while not canCreate(newPath):
        p = input('>> ')
        if not isValid(p):
            print(f'{RC}Path contains disallowed symbols{DC}')
            continue
        if os.path.exists(p):
            print(f'{RC}Path already exists{DC}')
            continue

        newPath = Path(p)
    
    return newPath
