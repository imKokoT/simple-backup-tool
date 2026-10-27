# CLI Arguments

> [!NOTE]
> Due to the current application design, argument positioning could be confusing, so there is a small explanation. However, changes may be made in the future.

In Box, the tool has two entry points: **operations** and **modules**. Modules implement specific features and can be invoked by **operations**.

## Operations

An operation defines a use case and acts as a *subcommand* in the CLI.

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
