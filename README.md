# Simple backup tool

A small CLI tool for making backups to your Google Drive cloud.

> [!WARNING]
> This documentation is in progress; it contains mistakes, deprecated information, and may change in the future!

# Features

- file-copy backups into a single archive
- config-based workflow setup
- powerful pattern search and filtering based on *gitwildmatch*
- several methods of compression
- backup encryption with AES or Chacha20Poly1305
- fully streamed backup/restore workflow from pack to final result
- an option to run the backup/restore workflow in RAM without affecting drive

# How to set up

## Requirements

- Supported systems: Windows, Linux
- Python 3.12+
- ~200MB of free space

## Setup

The project uses *pyproject.toml* for setup. To install the project, use:

```sh
# optionally for Windows, to prevent installing it globally
python -m venv .venv

# on Windows
.venv\Scripts\activate
# on Linux
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e .
```

After a successful installation, the entry script is:

```sh
sbt
```

There is also an option to expose the application to the user scope if the application was installed into a *venv*:

```sh
sbt manage install-launcher
```

If everything is working correctly, continue the setup with the [First Backup topic](/docs/First%20Backup.md).
