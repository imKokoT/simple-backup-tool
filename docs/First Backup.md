# First Backup

Before we continue, we must first create a [Google Drive service](./Create%20Google%20Service.md).

## Schema

The tool provides backup creation via **schemas**. A schema is a YAML file containing all configurations for both backup and restore workflows. Let's see its minimal structure:

```sh
sbt manage create-schema
```

The template you open will look something like this:

```yaml
credentials: your-secret

targets:
- /path/to/local/folder/or/file

destination: /path/on/the/cloud
```

After modifying the credentials, targets, and destination, save and exit. Note that the *destination* path will be created automatically in the cloud.

## Backup

Now we can start the backup operation with:

```sh
sbt backup your-schema-name
```

If everything was configured correctly, a local pack will be created and, after authorization, sent to Google Drive.

## Restore

An uploaded backup can be simply restored with the following command:

```sh
sbt --cloud cloud_google_drive --destination /path/on/the/cloud --credentials your-secret restore your-schema-name
```

The command looks a bit unusual, but the reason why is explained [here](./CLI%20Arguments.md). By default, the restore workflow requires user attention. After the archive is downloaded and unpacked, the tool will ask what to do with the data. There are a few possible ways to restore:

- **abort**: leave the local pack unpacked
- **restore to */restored* folder**
- **try to rewrite original data**: all failed targets will be placed in the */restored* folder or a user-specified path

The */restored* folder is located under the tool's tmp dir:

- **Windows**: `%localappdata%/simple-backup-tool/your-schema-name/`
- **Linux**: `$HOME/.local/state/simple-backup-tool/your-schema-name/`

This directory also contains the session cache, runtime files, etc. Learn more about the project's folders [here](./App%20folders.md).

## Advanced Workflows

The following topics will help you set up more complex workflows involving filtering, different compression methods, encryption, etc:

- [Automation](./Automation.md)
- [App folders](./App%20folders.md)
- [Backup with service account](./Backup%20With%20Service%20Account.md)
- [CLI arguments](./CLI%20Arguments.md)
- [Compression](./Compression.md)
- [Encryption](./Encryption.md)
- [Filtering](./Filtering.md)
- [Zero Waste Mode](./Zero%20Waste%20Mode.md)
- [FAQ]()
