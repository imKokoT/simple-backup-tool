import os
from pathlib import Path
import sys
import logging

from properties import *
from paths import getAppDir

logger = logging.getLogger(__name__)


def install(args):
    # select launcher path
    if sys.platform == 'win32':        
        template = 'res/templates/sbt.cmd'
        if DEBUG:
            scriptPath = Path('./sbt.cmd')
        else:
            scriptDir = getAppDir() / 'bin'
            scriptPath = scriptDir / 'sbt.cmd'
            os.makedirs(scriptDir, exist_ok=True)

        execPath = Path(sys.executable).parent / 'sbt.exe'
    elif sys.platform == 'linux':
        template = 'res/templates/sbt.sh'
        if DEBUG:
            scriptPath = Path('./sbt')
        else:
            os.makedirs(Path.home() / '.local' / 'bin', exist_ok=True)
            scriptPath = Path.home() / '.local' / 'bin' / 'sbt'

        execPath = Path(sys.executable).parent / 'sbt'
    else:
        logger.error(f'unsupported platform')
        exit(1)

    # register script into HKEY_CURRENT_USER\Environment\Path
    if sys.platform == 'win32' and not DEBUG:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "Environment", 0,
            winreg.KEY_READ | winreg.KEY_WRITE,
        ) as key:
            try:
                current, _ = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current = ""

            entries = [p for p in current.split(";") if p]

            if scriptDir not in entries:
                entries.append(scriptDir)

                winreg.SetValueEx(
                    key,
                    "Path",
                    0,
                    winreg.REG_EXPAND_SZ,
                    ";".join(entries),
                )
                logger.debug('registered script path into HKEY_CURRENT_USER\\Environment\\Path')

    # create launcher script
    with open(scriptPath, 'w', encoding='utf-8') as f:
        with open(template, 'r', encoding='utf-8') as t:
            f.write(t.read().format(
                app_dir=Path.cwd(),
                app_path = execPath
            ))

    if sys.platform == 'linux':
        scriptPath.chmod(0o755)

    print(f'{LGC}created launcher script {scriptPath.absolute()} successfully!{DC}')


def uninstall(args):
    # select launcher path
    if sys.platform == 'win32':
        if DEBUG:
            scriptPath = Path('./sbt.cmd')
        else:
            scriptPath = getAppDir() / 'bin' / 'sbt.cmd'
    elif sys.platform == 'linux':
        if DEBUG:
            scriptPath = Path('./sbt')
        else:
            scriptPath = Path.home() / '.local' / 'bin' / 'sbt'
    else:
        logger.error(f'unsupported platform')
        exit(1)

    # try to remove script from HKEY_CURRENT_USER\Environment\Path
    if sys.platform == 'win32' and not DEBUG:
        import winreg

        scriptDir = getAppDir() / 'bin'
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "Environment", 0, 
            winreg.KEY_READ | winreg.KEY_WRITE,
        ) as key:
            try:
                current, _ = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current = ""

            entries = [p for p in current.split(";") if p]

            if scriptDir in entries:
                entries.remove(scriptDir)

                winreg.SetValueEx(
                    key,
                    "Path",
                    0,
                    winreg.REG_EXPAND_SZ,
                    ";".join(entries),
                )
                logger.debug('removed script path from HKEY_CURRENT_USER\\Environment\\Path')

    # try to delete launcher file
    if scriptPath.exists():
        os.remove(scriptPath)
        print(f'{LGC}removed launcher script {scriptPath} successfully!{DC}')
    else:
        print(f'{RC}script {scriptPath} does not exists!{DC}')
