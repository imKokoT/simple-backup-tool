# Simple backup tool

A small CLI tool for making backups to your Google Drive cloud.

> [!WARNING]
> This documentation is in progress, contains mistakes, deprecated information and could be changed in the future!

# Features

- file copy backups into single archive
- config-based workflow setup
- powerful pattern search and filtering based on *gitwildmatch*
- several methods of compressing
- backup encryption with AES or Chacha20Poly1305
- fully streamed backup/restore workflow from pack to final result
- an option to start backup/restore workflow in RAM without affecting drive

# How to setup

## Requirements

- supported systems: Windows, Linux
- Python 3.12+
- ~200MB of free space

## Setup

Project uses *pyproject,toml* to setup. To install the project use:

```sh
# optionally, to prevent install it globally
python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e .
```

After success install there is entry script:

```sh
sbt
```

If everything is fine, we will continue setup with [First Backup topic](/docs/First%20Backup.md)
