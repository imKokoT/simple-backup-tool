import logging
import os
from pathlib import Path
import pathspec
from core.app_config import config
from properties import *

logger = logging.getLogger(__name__)


def isPatter(path:str) -> bool:
    return any(char in path for char in '!*?[]')


def searchTargets(pattern:str) -> list[str]:
    '''search for targets by a pattern'''
    out = []
    rootParts = []
    for p in Path(pattern).parts:
        if isPatter(p): 
            break
        
        rootParts.append(p)

    rootPath = Path('/'.join(rootParts).replace('//', '/'))
    targetPath = Path(pattern)
    patternPath = Path('/'.join(
        targetPath.parts[len(rootPath.parts):]
    ).replace('//', '/'))
    
    for path in Path(rootPath).rglob(patternPath):
        if path.is_symlink():
            logger.warning(f'skip target symlink {path}')
            continue
        out.append(str(path))

    logger.debug(f'found {len(out)} targets for pattern {pattern}')
    return out


def loadIgnorePatterns(directory:str) -> pathspec.PathSpec|None:
    patterns = []
    sbtignore = f'{directory}/.sbtignore'
    gitignore = f'{directory}/.gitignore'
    raw:list[str] = []
    
    if config.get('backup.load_gitignore') and os.path.exists(gitignore):
        logger.debug(f'found {gitignore}, loading ignore patterns...')
        with open(gitignore, 'r', encoding='utf-8') as f:
            raw += f.readlines()

    if os.path.exists(sbtignore):
        logger.debug(f'found {sbtignore}, loading ignore patterns...')
        with open(sbtignore, 'r', encoding='utf-8') as f:
            raw += f.readlines()

    for l in raw:
        l = l.strip()
        l = l.replace('\\', '/')
        patterns.append(l)
    if len(patterns) == 0:
        return
        
    try:
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    except ValueError as e:
        logger.warning(f'ignore patters of directory "{directory}" has wrong format, so skipped; error: {e}')


def shouldIgnore(path:Path, specStack:list[tuple[Path, pathspec.PathSpec]]) -> bool:
    for i in range(len(specStack) - 1, -1, -1):
        if not specStack[i]: continue
        specPath, spec = specStack[i]

        if spec.match_file(path.relative_to(specPath)):
            return True
    return False
