# Simple backup tool

A small CLI tool for making backups to your Google Drive cloud.

> [!WARNING]
> This documentation is in progress, contains mistakes, deprecated information and could be changed in the future!

# Features

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
