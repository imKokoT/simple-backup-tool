# Zero Waste Mode

The tool has a feature to save session files to RAM. This is could speed-up backup/restore workflows, make them more frequent and save your disk from wear. On the other hand, the feature is payed with decreased stability.

To enable this feature, edit app config:

```sh
sbt manage config
```

And change related setting `zero_waste` to `true`.

> [!WARNING]
> REQUIRES A HUGE AMOUNT OF RAM! Large backups/restores could cause freezes, crashes, system slowdown etc, if the system does not have enough RAM.
