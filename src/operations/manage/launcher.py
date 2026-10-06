import os
from pathlib import Path
import sys
import logging

from properties import *

logger = logging.getLogger(__name__)


def install(args):
    if sys.platform == 'win32':
        pass
    elif sys.platform == 'linux':
        if DEBUG:
            scriptPath = Path('./sbt')
        else:
            scriptPath = Path.home() / '.local' / 'bin' / 'sbt'

        with open(scriptPath, 'w', encoding='utf-8') as f:
            with open('res/templates/sbt.sh', 'r', encoding='utf-8') as t:
                f.write(t.read().format(
                    app_dir=Path.cwd(),
                    app_path=(Path(sys.prefix) / 'bin' / 'sbt').relative_to(Path.cwd())
                ))

        scriptPath.chmod(0o755)

        print(f'{LGC}created launcher script {scriptPath} successfully!{DC}')
    else:
        logger.error(f'unsupported platform')


def uninstall(args):
    if sys.platform == 'win32':
        pass
    elif sys.platform == 'linux':
        if DEBUG:
            scriptPath = Path('./sbt')
        else:
            scriptPath = Path.home() / '.local' / 'bin' / 'sbt'

        if scriptPath.exists():
            os.remove(scriptPath)
            print(f'{LGC}removed launcher script {scriptPath} successfully!{DC}')
        else:
            print(f'{RC}script {scriptPath} does not exists!{DC}')
    else:
        logger.error(f'unsupported platform')