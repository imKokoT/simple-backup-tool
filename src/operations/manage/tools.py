import shutil
import subprocess
import sys
import os
import logging

logger = logging.getLogger(__name__)


def openWithinEditor(path):
    if sys.platform == 'win32':
        os.startfile(path)
    elif sys.platform == 'linux':
        # display mode
        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            subprocess.run(["xdg-open", path], check=False)
        # headless mode
        else:
            executable = shutil.which("nano") or shutil.which("vi") or shutil.which("micro")
            if not executable:
                logger.error(f'failed open {path} to edit; no suitable editor')
                return
            
            subprocess.run(
                [executable, str(path)],
                check=False,
            )
    else:
        logger.error(f'failed open {path} to edit; unsupported platform')
