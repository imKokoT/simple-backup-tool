from pathlib import Path
import sysconfig
import subprocess
import sys


def run_sbt(*args: str) -> None:
    sbtPath = None
    if sys.platform == 'linux':
        sbtPath = Path(sysconfig.get_path("scripts")) / 'sbt'
    elif sys.platform == 'win32':
        sbtPath = Path(sysconfig.get_path("scripts")) / 'sbt.exe'
    else:
        raise NotImplementedError('unsupported system')

    result = subprocess.run(
        [sbtPath, '-v', *args],
        check=False,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("STDOUT:")
        print(result.stdout)

        print("STDERR:")
        print(result.stderr)

        raise subprocess.CalledProcessError(
            result.returncode,
            result.args,
        )
    