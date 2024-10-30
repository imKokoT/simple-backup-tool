import time
import pathspec
from config import *
from miscellaneous import getTMP


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

    folders = [os.path.join(
                    root, 
                    os.path.basename(folders[i])+f' ({hex(i)[2:]})') 
               for i in range(0, len(folders))]
    files = [os.path.join(
                root, 
                f'({hex(i)[2:]}) '+os.path.basename(files[i])) 
             for i in range(0, len(files))]

    packConfig['folders'] = folders
    packConfig['files'] = files
    