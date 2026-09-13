import os
import platform
from properties import *
from pathlib import Path


def getAppDir() -> Path:
    """
    Return the application data directory.

    Windows: 
        `%%appdata%%/[COPYRIGHT]/simple-backup-tool`
    
    Linux: 
        `$HOME/.local/share/[COPYRIGHT]/simple-backup-tool`
    
    In DEBUG mode, returns the `<project root directory>/configs`.
    """
    system = platform.system()

    if DEBUG:
        path = Path(__file__).resolve().parent.parent / 'configs'
    elif system == "Windows":
        base = os.getenv("APPDATA")
        if not base:
            raise RuntimeError("APPDATA not set")
        path = Path(base) / COPYRIGHT / "simple-backup-tool"
    elif system == "Linux":
        path = Path.home() / ".local" / "share" / COPYRIGHT / "simple-backup-tool"
    else:
        raise NotImplementedError(f"Unsupported OS: {system}")

    path.mkdir(parents=True, exist_ok=True)
    return path


def getTmpDir() -> Path:
    """
    Returns directory for temporal files

    Windows:
        `%localappdata%/[COPYRIGHT]/simple-backup-tool`

    Linux:
        `$HOME/.local/state/[COPYRIGHT]/simple-backup-tool`

    In DEBUG mode, returns the `<project root directory>/configs/tmp
    """
    system = platform.system()

    if DEBUG:
        path = Path(__file__).resolve().parent.parent / 'configs' / 'tmp'
    else:
        if system == "Linux":
            path = Path.home() / ".local" / "state"/ COPYRIGHT / "simple-backup-tool"

        elif system == "Windows":
            base = os.getenv("LOCALAPPDATA")
            if not base:
                raise RuntimeError("APPDATA not set")
            path = Path(base) / COPYRIGHT / "simple-backup-tool"

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
