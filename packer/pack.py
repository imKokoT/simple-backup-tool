import os
from pathlib import Path
import tarfile
import pathspec
from properties import *
from logger import logger
from miscellaneous.miscellaneous import getTMP, humanSize, iprint
from packer.packconfig import configurePack
from packer.tools import loadIgnorePatterns, shouldIgnore, dumpPackedTargetsLog
from runtime_data import rtd


def packAll():
    logger.info('packing process started')
    
    schema:dict = rtd['schema']
    ignore = schema.get('ignore', '')
    schemaName = schema.get('__name__')

    if not schema: 
        logger.fatal(f'packing process failed: no schema "{schemaName}"')
        exit(1)
    
    tmp = getTMP()

    archive = tarfile.open(f'{tmp}/{schemaName}.tar', 'w')
    
    if not schema.get('targets'):
        logger.fatal(f'failed to get "targets" key from schema "{schemaName}"')
        exit(1)

    packedCount = 0
    packedTargets = []
    result = {
        'files':0,
        'ignored': 0,
        'size': 0,
        'scannedSize': 0,

        # {target: [packed file paths] or (packed file paths,)}
        'filePaths': {}
    }
    res:dict
    packFile.counter = 0
    packFolder.counter = 0
    for target in schema['targets']:
        if os.path.isfile(target):
            res = packFile(target, archive)
        else:
            res = packFolder(target, archive, ignore)

        if res:
            packedTargets.append(target)
        
            result['files'] += res['files']
            result['ignored'] += res['ignored']
            result['scannedSize'] += res['scannedSize']
            result['size'] += res['size']
            result['filePaths'].update(res['filePaths'])
            packedCount += 1

    configurePack(archive, schema, packedTargets)

    dumpPackedTargetsLog(result['filePaths'])
    logger.info(f'packing process finished successfully;\n'
                       f' - packs created: {packedCount}/{len(schema["targets"])}\n'
                       f' - archived and ignored total files: {result['files']}/{result['ignored']}\n'
                       f' - archived total size: {humanSize(result["size"])}/{humanSize(result["scannedSize"])}'
                       )
    archive.close()


def packFolder(targetFolder:str, archive:tarfile.TarFile, ignore:str):
    if not os.path.exists(targetFolder):
        logger.error(f'packing failed: target folder "{targetFolder}" not exists')
        return

    logger.info(f'packing target folder "{targetFolder}"; reading content...')
    files:list[Path] = []
    scanned = 0
    ignored = 0
    scannedSize = 0
    packSize = 0

    GLOBAL = '.'
    specStack = [(GLOBAL, pathspec.PathSpec.from_lines('gitignore', ignore.splitlines()))]  # (path, spec) or None
    pathStack = [(Path(targetFolder), 1)]                                                   # (path, depth)

    while pathStack:
        current, depth = pathStack.pop()

        while len(specStack) > depth:
            specStack.pop()

        isIgnored = shouldIgnore(current.relative_to(targetFolder), specStack)

        if not current.is_dir():
            if isIgnored:
                ignored += 1
            else:
                files.append(current)
                scannedSize += os.path.getsize(current)
            scanned += 1

            iprint(f'{scanned}/{ignored} files scanned/ignored')
            continue
        else:
            if isIgnored:
                continue
            spec = loadIgnorePatterns(current)
            if spec:
                specStack.append((current.relative_to(targetFolder), spec))
            else:
                specStack.append(None)

            with os.scandir(current) as it:
                for entry in it:
                    pathStack.append((Path(entry), depth + 1))
    
    for p in files:
        packSize += os.path.getsize(p)

    logger.info(f'reading success; total files: {len(files)} [{humanSize(packSize)}/{humanSize(scannedSize)}]; ignored total: {ignored}')    

    logger.info(f'adding to archive...')
    
    for fp in files:
        dpath = f'folders/{hex(packFolder.counter)[2:]}/{fp.relative_to(targetFolder)}'
        archive.add(fp, arcname=dpath)
    
    logger.info(f'success')
    return {
        'files':len(files),
        'ignored': ignored,
        'size': packSize,
        'scannedSize': scannedSize,
        'filePaths': {targetFolder: tuple(files)}
    }


def packFile(targetFile:str, archive:tarfile.TarFile):
    if not os.path.exists(targetFile):
        logger.error(f'packing failed: target file "{targetFile}" not exists')
        return
    logger.info(f'packing target file "{targetFile}"')

    size = os.path.getsize(targetFile)

    archive.add(targetFile, f'files/{hex(packFile.counter)[2:]}')
    packFile.counter += 1
    return {
        'files': 1,
        'ignored': 0,
        'size': size,
        'scannedSize': size,
        'filePaths': {targetFile: (Path(targetFile),)}
    }
