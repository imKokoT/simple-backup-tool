import os
import time
import pathspec
from app_config import Config
from properties import *
from miscellaneous import getTMP
from logger import logger


def loadIgnorePatterns(directory:str) -> pathspec.PathSpec|None:
    patterns = []

    for dpath, _, _ in os.walk(directory):
        ignoreFilers =(
            os.path.join(dpath, '.sbtignore'),
            os.path.join(dpath, '.gitignore')
        )
        for ignoreF in ignoreFilers:
            if not os.path.exists(ignoreF) or not Config().include_gitignore and os.path.basename(ignoreF) == '.gitignore': continue
            
            with open(ignoreF, 'r', encoding='utf-8') as f:
                for l in f.readlines():
                    l = l.strip()
                    l = f'!{l.replace('!', '')}' if '!' in l else l
                    l = f'{dpath[len(directory):]}/{'**/'+l if not l.startswith('/') else l}'
                    l = l.replace('\\', '/')
                    patterns.append(l)
        if len(patterns) == 0:
            return

    return pathspec.PathSpec.from_lines('gitignore', patterns)


def shouldIgnore(path:str, specs:dict[str,pathspec.PathSpec], sorted_specs:list) -> bool:
    specPath = next(filter(lambda d: path.startswith(d), sorted_specs), None)
    spec = specs.get(specPath)
    return spec and spec.match_file(path[len(specPath):])


def dumpRestoredLog(packConfig:dict, schema):
    tmp = getTMP()
    root = f'{tmp}/restored/{schema['__name__']}'

    folders = packConfig['folders']
    files = packConfig['files']

    with open(f'{root}/dump.log', 'w', encoding='utf-8') as f:
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


def modifyRestorePaths(packConfig:dict, schema):
    tmp = getTMP()
    root = f'{tmp}/restored/{schema['__name__']}'

    folders = packConfig['folders']
    files = packConfig['files']

    folders = [modifySingleRestorePath(p, schema, packConfig, True) for p in folders]
    files = [modifySingleRestorePath(p, schema, packConfig, False) for p in files]

    packConfig['folders'] = folders
    packConfig['files'] = files


def modifySingleRestorePath(path:str, schema:dict, packConfig:dict, isFolder:bool) -> str:
    tmp = getTMP()
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

    newPath = os.path.join(root, newName)

    return newPath
