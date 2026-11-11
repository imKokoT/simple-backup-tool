import subprocess
import sys
from pathlib import Path
from tests.integration.tools import run_sbt

from core.paths import getAppDir


def launcher_path() -> Path:
    if sys.platform == 'win32':
        return getAppDir() / 'bin' / 'sbt.cmd'
    elif sys.platform == 'linux':
        return Path.home() / '.local' / 'bin' / 'sbt'
    else:
        raise NotImplementedError(f'unsupported system "{sys.platform}"')


def test_launcher_install_and_uninstall(tmp_path, monkeypatch):
    if sys.platform == 'win32':
        monkeypatch.setenv("APPDATA", str(tmp_path))
    elif sys.platform == 'linux':
        monkeypatch.setenv("HOME", str(tmp_path))

    path = launcher_path()

    # Clean up from a previous failed test.
    if path.exists():
        run_sbt("manage", "uninstall-launcher")

    assert not path.exists()

    # Install
    run_sbt("manage", "install-launcher")

    assert path.exists()
    assert path.is_file()

    if sys.platform == "win32":
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
        ) as key:
            path_value, _ = winreg.QueryValueEx(key, "Path")

        expected = str(getAppDir() / "bin")

        assert expected.lower() in {
            entry.lower()
            for entry in path_value.split(";")
            if entry
        }

    # execute the installed launcher.
    with open(path, 'r') as f:
        print(f'GENERATED SCRIPT:\n{f.read()}\n')

    result = subprocess.run(
        [str(path)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip()

    # Uninstall
    run_sbt("manage", "uninstall-launcher")

    assert not path.exists()
    
    if sys.platform == "win32":
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
        ) as key:
            path_value, _ = winreg.QueryValueEx(key, "Path")

        expected = str(getAppDir() / "bin")

        assert expected.lower() not in {
            entry.lower()
            for entry in path_value.split(";")
            if entry
        }
