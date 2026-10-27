# Compression

The tool provides a wide range of compression formats. Besides this, it natively supports the [7z archiver](https://7-zip.org/). However, the tool also allows the use of external archivers through the CLI, if they support stdin/stdout mode.

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
