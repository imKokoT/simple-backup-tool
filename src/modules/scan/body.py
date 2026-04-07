from core.app_config import config
from core.cli import iprint
from core.context import ctx
from paths import getTmpDir
from .tools import *
import logging
import pathspec
import os
from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from modules.scan import ScanModule

logger = logging.getLogger(__name__)


def entry():
    module:ScanModule = ctx.currentModule
    schema = ctx.schema
    args = ctx.args

    targets = schema.get('targets')

    tmpDir = getTmpDir() / schema.name
    tmpDir.mkdir(parents=True, exist_ok=True)

    # scan targets
    for target in targets:
        if os.path.isfile(target):
            scanFile(target)
        else:
            scanFolder(target)

    # write scan cache
    print('0')

def scanFile(target:Path):
    module:ScanModule = ctx.currentModule
    
    if not os.path.exists(target):
        logger.error(f'target file "{target}" not exists')
        return
    logger.info(f'scanned target file "{target}"')

    size = os.path.getsize(target)
    module.countedSize += size
    module.scannedSize += size
    module.counted += 1
    module.files.append(target)


def scanFolder(target:Path):
    module:ScanModule = ctx.currentModule
    schema = ctx.schema

    ignore:list[str] = schema.get('ignore')

    if not os.path.exists(target):
        logger.error(f'target folder "{target}" not exists')
        return

    logger.info(f'scanning target folder "{target}"...')
    files:list[Path] = []
    scanned = 0
    ignoredFiles = 0
    ignoredFolders = 0
    scannedSize = 0
    countedSize = 0

    GLOBAL = '.'
    specStack = [(GLOBAL, pathspec.PathSpec.from_lines('gitignore', ignore))]  # (path, spec) or None
    pathStack = [(Path(target), 1)]                                            # (path, depth)

    while pathStack:
        current, depth = pathStack.pop()

        while len(specStack) > depth:
            specStack.pop()

        isIgnored = shouldIgnore(current.relative_to(target), specStack)

        # file
        if not current.is_dir():
            if isIgnored:
                ignoredFiles += 1
            else:
                files.append(current)
            scannedSize += os.path.getsize(current)
            scanned += 1

            iprint(f'{scanned}/{ignoredFiles} files scanned/ignored')
            continue
        # folder
        else:
            if isIgnored:
                ignoredFolders += 1
                continue
            spec = loadIgnorePatterns(current)
            if spec:
                specStack.append((current.relative_to(target), spec))
            else:
                specStack.append(None)

            with os.scandir(current) as it:
                for entry in it:
                    pathStack.append((Path(entry), depth + 1))
    print()

    for p in files:
        countedSize += os.path.getsize(p)

    # TODO: humanSizes
    # logger.info(f'reading success; total files: {len(files)} [{humanSize(countedSize)}/{humanSize(scannedSize)}]; ignored total: {ignored}')
    logger.info(f'total files: {len(files)} [{countedSize}/{scannedSize}]; ignored total: {ignoredFiles}')
    
    logger.debug(f'record folder stats to module')
    module.countedSize += countedSize
    module.scannedSize += scannedSize
    module.ignoredFiles += ignoredFiles
    module.counted += len(files)
    module.folders.append(tuple(files))
