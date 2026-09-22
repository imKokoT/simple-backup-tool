# CLI Arguments

Due to current application design the argument positioning could be confusing, so there is a small explanation. However, in the future there will be possible changes.

In box the tool has entry points **operations** and **modules**, that implement some feature and could be invoked by **operations**.

## Operations

Operation defines some use-case and in CLI is a *subcommand*.

Example:

```sh
sbt backup  # invokes backup operation
```

Operation could have its *options*, *positional arguments* and etc.

Example:
```sh
sbt backup schema_name  # schema_name is required positional argument by this operation
```

## Modules

Module is implementation of some feature and is controlled by **operation**. As an example *scan module* that implements tool's searching/filtering mechanisms. Although modules can consume **operations'** arguments, they also could define own global-scope arguments. So that modules' arguments must be written **before an operation subcommand**.

Example:

```sh
sbt --locally backup some-schema  # --locally is an option of 'cloud' module 
```
