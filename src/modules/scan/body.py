from io import TextIOWrapper
from core.app_config import config
from core.cli import iprint
from core.context import ctx
from core.vfs import VFile
from paths import getTmpDir
from .tools import *
import logging
import pathspec
import os
import gzip
import json
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
    for target in sorted(targets):
        if os.path.isfile(target):
            scanFile(target)
        else:
            scanFolder(target)

    # TODO: human sizes
    logger.info(
        f'SCANNED TOTAL:\n'
        f' - scanned files: {module.scanned}\n'
        f' - included and ignored files: {module.included}/{module.ignoredFiles}\n'
        f' - ignored folders: {module.ignoredFolders}\n'
        f' - included/scanned size: {module.includedSize}/{module.scannedSize}'
    )

    scancachePath = getTmpDir() / schema.name / 'scanhash'
    if not scancachePath.exists():
        dumpScanCache()
        return

    with VFile(scancachePath, 'r', location='disk') as vf:
        if module.scanhash.hexdigest() == vf.read().decode():
            logger.info('No changes detected since last scan')

            if not args.force:
                logger.info('aborting...')
                quit(0)
    
    dumpScanCache()


def scanFile(target:str):
    module:ScanModule = ctx.currentModule
    
    if not os.path.exists(target):
        logger.error(f'target file "{target}" not exists')
        return
    logger.info(f'scanned target file "{target}"')

    stat = os.stat(target)
    size = stat.st_size
    module.includedSize += size
    module.scannedSize += size
    module.included += 1
    module.files.append(target)

    # count hash
    module.scanhash.update(target.encode())
    module.scanhash.update(str(size).encode())
    module.scanhash.update(str(stat.st_mtime).encode())


def scanFolder(target:str):
    module:ScanModule = ctx.currentModule
    schema = ctx.schema

    ignore:str = schema.get('ignore')

    if not os.path.exists(target):
        logger.error(f'target folder "{target}" not exists')
        return

    logger.info(f'scanning target folder "{target}"...')
    files:list[str] = []
    scanned = 0
    ignoredFiles = 0
    ignoredFolders = 0
    scannedSize = 0
    countedSize = 0

    GLOBAL = '.'
    specStack = [(GLOBAL, pathspec.PathSpec.from_lines('gitignore', ignore.splitlines()))]  # (path, spec) or None
    pathStack = [(Path(target), 1)]                                                         # (path, depth)

    while pathStack:
        current, depth = pathStack.pop()

        while len(specStack) > depth:
            specStack.pop()

        isIgnored = shouldIgnore(current.relative_to(target), specStack)

        # file
        if not current.is_dir():
            stat = current.stat()
            size = stat.st_size

            if isIgnored:
                ignoredFiles += 1
            else:
                rp = str(current.relative_to(target))
                files.append(rp)
                countedSize += size
                # count hash
                module.scanhash.update(rp.encode())
                module.scanhash.update(str(size).encode())
                module.scanhash.update(str(stat.st_mtime).encode())
            
            scannedSize += size
            scanned += 1
            iprint(f'{scanned}/{ignoredFiles}|{ignoredFolders} files scanned/ignored files|folders')
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

            # push folders to stack
            with os.scandir(current) as it:
                for entry in it:
                    pathStack.append((Path(entry), depth + 1))
    print()

    # TODO: humanSizes
    # logger.info(f'reading success; total files: {len(files)} [{humanSize(countedSize)}/{humanSize(scannedSize)}]; ignored total: {ignored}')
    logger.info(f'total files: {len(files)} [{countedSize}/{scannedSize}]; ignored total: {ignoredFiles} files / {ignoredFolders} folders')
    
    logger.debug(f'record folder stats to module')
    module.includedSize += countedSize
    module.scannedSize += scannedSize
    module.ignoredFiles += ignoredFiles
    module.ignoredFolders += ignoredFolders
    module.included += len(files)
    module.scanned += scanned
    module.foldersFiles.append(tuple(files))
    module.folders.append(target)


def dumpScanCache():
    module:ScanModule = ctx.currentModule
    schema = ctx.schema
    
    tmpDir = getTmpDir() / schema.name
    cachePath = tmpDir / 'scancache'
    hashPath = tmpDir / 'scanhash'

    logger.debug(f'dump scan cache to {cachePath}')
    cache = {
        'meta': {
            'scanhash': module.scanhash.hexdigest(),
            'session': ctx.sessionTime
        },
        'folders': module.folders,
        'foldersFiles': module.foldersFiles,
        'files': module.files
    }

    with VFile(cachePath, 'w') as vf:
        if DEBUG:
            with TextIOWrapper(vf, encoding="utf-8") as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
        else:
            with gzip.GzipFile(fileobj=vf, mode="wb") as gz:
                with TextIOWrapper(gz, encoding="utf-8") as f:
                    json.dump(cache, f, ensure_ascii=False, separators=(',', ':'))

    with VFile(hashPath, 'w', location='disk') as vf:
        vf.write(module.scanhash.hexdigest().encode())
