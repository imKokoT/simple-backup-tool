# Filtering

The tool supports powerful, easy-to-setup gitignore-like patterns. Filtering could be useful to select or exclude files/folders from backup, to reduce space usage and increase packing speed.

## Schema Params

```yaml
ignore: ...    # global ignore patterns
targets: []    # targets also support patters, but with limitations
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

We also specify which targets to pack to an archive with `targets` param. Although we usually specify which folders/files to pack, there is an option to use patterns too, **BUT** with limitations and possible problems.

Example:

```yaml
# this parameter is required by default
targets:
- /path/to/your/folder/
- /path/to/your/file.txt
- /searching/pattern/*/path/*.png
```

> [!WARNING]
> `targets` patters usually cause packing duplicates, bloating of the pack size, low performance, crashes etc! Wrongly constructed patters could make pack uneffecient to restore! 
>
> **DO NOT** write global search patters blindly! Usually it is not a good idea to use patters for searing files, because the tool threats them as separate targets! **Regular targets still preferred**, use patterns in spacial cases only!
>
> ```yaml
> targets:
> - '*.png'  # very bad; causes huge amount of single file targets
> - '/some/path/*'  # bad; use simple /some/path/
> - '/some/path/*.png'  # also could be bad
> - '/some/path/*/saves_2026.??'  # yes; exposes to targets .../saves folders
> - '/some/path/*.db*'  # yes if you know that few of these files somewhere under /some/path
> ```

## .sbtignore & .gitignore

There is also an option to filter folders/files within specific file `.sbtignore`. It fully inherits `.gitignore` functionality. Created `.sbtignore` file under some *target path* will filter targets under this *target path*.

> [!WARNING]
> As mentioned before `ignore` parameter works globally, overlapping any `.sbtignore` patterns

Nevertheless `.sbtignore` is usually enough, there is also an option to load `.gitignore` files to. This is disabled by default, so edit app's config:

```sh 
sbt manage config
```

And modify value of related parameter. `.sbtignore` still has higher load priority, so with it you can disable some `.gitignore` items from excluding.
