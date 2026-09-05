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
                       f'{'\n'.join([f' - {f}\t[FOLDER]' for f in module.packConfig.targetFolders])}\n'
                       f'{'\n'.join([f' - {f}\t[FILE]' for f in module.packConfig.targetFiles])}\n'):
        if getConfirm('y', f'Do you want to restore data into {module.restoredFolder}'):
            module.restoreToRestored = True 
        else:
            exit(0)

    unpack_files()
    unpack_folders()

    module.pack.close()


def unpack_files():
    module:UnpackerModule = ctx.currentModule

    for tf in module.packConfig.targetFiles:
        path = selectRestorePath(Path(tf), 'file')
        module.pack.restore_file(module.packConfig, tf, path)
        logger.info(f'restored file "{tf}" to {path}')


def unpack_folders():
    module:UnpackerModule = ctx.currentModule

    for tf in module.packConfig.targetFolders:
        logger.info(f'restoring folder "{tf}"')
        path = selectRestorePath(Path(tf), 'folder')
        module.pack.restore_folder(module.packConfig, tf, path)


def selectRestorePath(path:Path, tType) -> Path:
    module:UnpackerModule = ctx.currentModule

    # if selected restore to restored folder
    if module.restoreToRestored:
        i = module.packConfig.targetFiles.index(str(path.resolve())) if tType == 'file' \
            else module.packConfig.targetFolders.index(str(path.resolve()))
        path = module.restoredFolder / f'{path.name} ({hex(i)[2:]})'
        return path

    # interactive select
    if not path.parent.exists():
        if config.get('restore.restore_to_restored_if_path_invalid'):
            i = module.packConfig.targetFiles.index(str(path.resolve())) if tType == 'file' \
                else module.packConfig.targetFolders.index(str(path.resolve()))
            path = module.restoredFolder / f'{path.name} ({hex(i)[2:]})'
        else:
            # ask user where to restore file
            path = askAnotherPath(path)
            if not path:
                logger.info(f'skip folder {path}')
                path
    else:
        fName = f"{path.stem}-restored{path.suffix}" if fName == 'file' else f"{path.stem}-restored"
        path = path if config.get('restore.allow_local_replace') else path.with_name(fName)

    return path


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
