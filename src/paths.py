import os
import platform
from properties import *
from pathlib import Path


def get_app_dir() -> Path:
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
