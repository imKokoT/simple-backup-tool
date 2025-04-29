import os
from pathlib import Path
import time
import pathspec
from app_config import Config
from properties import *
from miscellaneous.miscellaneous import getTMP
from logger import logger
from runtime_data import rtd


def loadIgnorePatterns(directory:str) -> pathspec.PathSpec|None:
    patterns = []

    ignoreFilers =(
        f'{directory}/.sbtignore',
        f'{directory}/.gitignore'
    )
    for ignoreF in ignoreFilers:
        if not os.path.exists(ignoreF) or not Config().include_gitignore and os.path.basename(ignoreF) == '.gitignore': continue

        logger.debug(f'found {ignoreF}, loading ignore patterns...')

        with open(ignoreF, 'r', encoding='utf-8') as f:
            for l in f.readlines():
                l = l.strip()
                # l = f'!{l.replace('!', '')}' if '!' in l else l
                # l = f'{directory[len(directory):]}/{'**/'+l if not l.startswith('/') else l}'
                # l = l.replace('//', '/')
                l = l.replace('\\', '/')
                patterns.append(l)
    if len(patterns) == 0:
        return
        
    try:
        logger.debug('building pathspec')
        return pathspec.PathSpec.from_lines('gitignore', patterns)
    except ValueError as e:
        logger.warning(f'ignore patters of directory "{directory}" has wrong format, so skipped; error: {e}')


def shouldIgnore(path:str, specStack:list[tuple[Path, pathspec.PathSpec]]) -> bool:
    return
    specPath = next(filter(lambda d: path.startswith(d), sorted_specs), None)
    spec = specs.get(specPath)
    return spec and spec.match_file(path[len(specPath):])


## TODO: for now shows only what pack contains, not what has really restored 
def dumpRestoredLog(packConfig:dict):
    schema:dict = rtd['schema']
    folders = packConfig['folders']
    files = packConfig['files']

    with open(f'logs/restored-targets_{schema['__name__']}.log', 'w', encoding='utf-8') as f:
        f.write(f'DUMP CREATED OF RESTORED BACKUP "{schema['__name__']}"\n'
                f'\n'
                f'dump time at {time.ctime()}\n'
                f'backup created at {time.ctime(packConfig['creation-time'])}\n\n'
                )
        f.write('FOLDERS:\n')
        i = 0
        for folder in folders:
            f.write(f' {hex(i)[2:]}\t {folder}\n')
            i += 1
        f.write('FILES:\n')
        i = 0
        for file in files:
            f.write(f' {hex(i)[2:]}\t {file}\n')
            i += 1


def dumpPackedTargetsLog(filePaths:dict[str,tuple]):
    schema:dict = rtd['schema']
    logger.debug(f'dump packed files to "logs/packed-files_{schema['__name__']}.log"')
    df = open(f'logs/packed-files_{schema['__name__']}.log', 'w', encoding='utf-8')

    df.write(f'PACKED FILES DUMP\n\n'
             f'SCHEMA: {schema['__name__']}\n'
             f'TIME: {time.ctime()}\n\n')
    
    for k, v in filePaths.items():
        df.write(f'TAR {k}:\n')
        for p in v:
            df.write(f'\t{p}\n')
        df.write('\n')

    df.close()


def modifyRestorePaths(packConfig:dict):
    tmp = getTMP()
    schema:dict = rtd['schema']
    root = f'{tmp}/restored/{schema['__name__']}'

    folders = packConfig['folders']
    files = packConfig['files']

    folders = [modifySingleRestorePath(p, packConfig, True) for p in folders]
    files = [modifySingleRestorePath(p, packConfig, False) for p in files]

    packConfig['folders'] = folders
    packConfig['files'] = files


def modifySingleRestorePath(path:str, packConfig:dict, isFolder:bool) -> str:
    tmp = getTMP()
    schema:dict = rtd['schema']
    root = f'{tmp}/restored/{schema['__name__']}'

    i = packConfig['folders'].index(path) if isFolder else packConfig['files'].index(path)

    if os.path.isdir(path):
        newName = os.path.basename(path)+f' ({hex(i)[2:]})'
    else:
        baseName = os.path.basename(path).split('.')
        if len(baseName) > 1:
            name = baseName[0]
            ext = '.'+baseName[-1]
        else:
            name = baseName[0]
            ext = ''
        newName = f'{name} ({hex(i)[2:]}){ext}'

    newPath = f'{root}/{newName}'

    return newPath
