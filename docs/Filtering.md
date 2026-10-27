# Filtering

The tool supports powerful, easy-to-set-up gitignore-like patterns. Filtering can be useful to select or exclude files/folders from backup to reduce space usage and increase packing speed.

## Schema Params

```yaml
ignore: ...    # global ignore patterns
targets: []    # targets also support patterns, but with limitations
```

## Global Filter

### Ignore

Global filtering can be set up with the `ignore` param. Everything in the `ignore` param will be excluded from packing.

Example:

```yaml
ignore: |
  *.log
  cache/
  home/Downloads/
```

### Targets

We also specify which targets to pack into an archive with the `targets` param. Although we usually specify which folders/files to pack, there is an option to use patterns too, **BUT** with limitations and possible problems.

Example:

```yaml
# this parameter is required by default
targets:
- /path/to/your/folder/
- /path/to/your/file.txt
- /searching/pattern/*/path/*.png
```

> [!WARNING]
> `targets` patterns usually cause packing duplicates, bloating of the pack size, low performance, crashes, etc.! Wrongly constructed patterns could make the pack inefficient to restore! 
>
> **DO NOT** write global search patterns blindly! Usually, it is not a good idea to use patterns for searching files, because the tool treats them as separate targets! **Regular targets are still preferred**; use patterns in special cases only!
>
> ```yaml
> targets:
> - '*.png'  # very bad; causes a huge amount of single-file targets
> - '/some/path/*'  # bad; use simple /some/path/
> - '/some/path/*.png'  # also could be bad
> - '/some/path/*/saves_2026.??'  # yes; exposes targets in .../saves folders
> - '/some/path/*.db*'  # yes, if you know that only a few of these files exist under /some/path
> ```

## .sbtignore & .gitignore

There is also an option to filter folders/files within a specific `.sbtignore` file. It fully inherits `.gitignore` functionality. A `.sbtignore` file created under a *target path* will filter targets under that *target path*.

> [!WARNING]
> As mentioned before, the `ignore` parameter works globally, overriding any `.sbtignore` patterns.

Nevertheless, while `.sbtignore` is usually enough, there is also an option to load `.gitignore` files too. This is disabled by default, so edit the app's config:

```sh 
sbt manage config
```

And modify the value of the related parameter `backup.load_gitignore`. `.sbtignore` still has higher priority, so you can use it to re-include items that were excluded by `.gitignore`.
