import os
import platform
from properties import *
from pathlib import Path


def getAppDir() -> Path:
    """
    Return the application data directory.

    Windows: 
        `%%appdata%%/simple-backup-tool`
    
    Linux: 
        `$HOME/.config/simple-backup-tool`
    
    In DEBUG mode, returns the `<project root directory>/configs`.
    """
    system = platform.system()

    if DEBUG:
        path = Path(__file__).resolve().parent.parent.parent / 'configs'
    elif system == "Windows":
        base = os.getenv("APPDATA")
        if not base:
            raise RuntimeError("APPDATA not set")
        path = Path(base) / "simple-backup-tool"
    elif system == "Linux":
        path = Path.home() / ".config" / "simple-backup-tool"
    else:
        raise NotImplementedError(f"Unsupported OS: {system}")

    path.mkdir(parents=True, exist_ok=True)
    return path


def getTmpDir() -> Path:
    """
    Returns directory for temporal files

    Windows:
        `%localappdata%/simple-backup-tool`

    Linux:
        `$HOME/.local/state/simple-backup-tool`

    In DEBUG mode, returns the `<project root directory>/configs/tmp
    """
    system = platform.system()

    if DEBUG:
        path = Path(__file__).resolve().parent.parent.parent / 'configs' / 'tmp'

    elif system == "Linux":
        path = Path.home() / ".local" / "state" / "simple-backup-tool"

    elif system == "Windows":
        base = os.getenv("LOCALAPPDATA")
        if not base:
            raise RuntimeError("APPDATA not set")
        path = Path(base) / "simple-backup-tool"

    else:
        raise NotImplementedError(f"Unsupported OS: {system}")

    path.mkdir(parents=True, exist_ok=True)
    return path


def canCreate(path:Path) -> bool:
    return path.parent.exists() and \
           path.parent.is_dir() and \
           os.access(path.parent, os.W_OK) and \
           not path.exists()


def isValid(path:str|Path) -> bool:
    if isinstance(path, str):
        path = Path(path)

    try:
        path.resolve(strict=False)
        return True
    except (OSError, ValueError):
        return False
