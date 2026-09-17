# Filtering

The tool supports powerful, easy-to-setup gitignore-like patterns. Filtering could be useful to select or exclude files/folders from backup, to reduce space usage and increase packing speed.

## Schema Params

```yaml
ignore: ...    # global ignore patterns
targets: ...   # targets also support patters, but with limitations
```

## Global Filter

### Ignore

Global filtering could be setup with `ignore` param. Everything in `ignore` param will be excluded from packing.

Example:

```yaml
ignore: |
  *.log
  cache/
  home/Downloads/
```

### Targets

We also specify which targets to pack to an archive with `targets` param.

Example:

```yaml
# this parameter is required by default
targets:
- path/to/your/folder/
- path/to/your/file.txt
```

## .sbtignore & .gitignore

There is also an option to filter folders/files within specific file `.sbtignore`. It fully inherits `.gitignore` functionality. Created `.sbtignore` file under some *target path* will filter targets under this *target path*.

> [!WARNING]
> As mentioned before `ignore` parameter works globally, overlapping any `.sbtignore` patters

Nevertheless `.sbtignore` is usually enough, there is also an option to load `.gitignore` files to. This is disabled by default, so edit app's config:

```sh 
sbt manage config
```

And modify value of related parameter. `.sbtignore` still has higher load priority, so with it you can disable some `.gitignore` items from excluding.
