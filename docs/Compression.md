# Compression

The tool provides wide range of compression formats. Beside this it natively supports [7z archiver](https://7-zip.org/). However, the tool also allows to use external archivers through CLI, if they support stdin/stdout mode.

## Schema Params

```yaml
# default values
packer.archiver: internal # Which archiver to use
packer.format: gz         # Compression formate
packer.level: 5           # Compression level
```

## Build-in Internal Archiver

Default tool's archiver, based on compressed or pure TAR. Supports several formats from a box.

```yaml
packer.archiver: internal
```

Supports: `tar`, `gz`, `xz`, `bz2`, `zst` (Python 3.14+)

## 7zip Archiver

External [7z archiver](https://7-zip.org/). To use it, it must be accessible from `PATH` environment variable.

```yaml
packer.archiver: 7zip
```
