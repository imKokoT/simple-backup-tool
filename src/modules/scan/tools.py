import logging
import os
from pathlib import Path
import pathspec
from properties import *

logger = logging.getLogger(__name__)

# TODO: optimize
def loadIgnorePatterns(directory:Path) -> pathspec.PathSpec|None:
    patterns = []

    ignoreFilers =(
        f'{directory}/.sbtignore',
        f'{directory}/.gitignore'
    )
    
    # TODO: config include_gitignore
    if not os.path.exists(ignoreFilers[0]):
        return
    logger.debug(f'found {ignoreFilers[0]}, loading ignore patterns...')

    with open(ignoreFilers[0], 'r', encoding='utf-8') as f:
        for l in f.readlines():
            l = l.strip()
            l = l.replace('\\', '/')
            patterns.append(l)
    if len(patterns) == 0:
        return
        
    try:
        return pathspec.PathSpec.from_lines('gitignore', patterns)
    except ValueError as e:
        logger.warning(f'ignore patters of directory "{directory}" has wrong format, so skipped; error: {e}')


def shouldIgnore(path:Path, specStack:list[tuple[Path, pathspec.PathSpec]]) -> bool:
    for i in range(len(specStack) - 1, -1, -1):
        if not specStack[i]: continue
        specPath, spec = specStack[i]

        if spec.match_file(path.relative_to(specPath)):
            return True
    return False
