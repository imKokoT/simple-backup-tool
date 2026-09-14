# First Backup

Before we continue, firstly we must create [Google Drive service](./Create%20Google%20Service.md)

## Schema

The tool provide creation of backups by **schemas**. Schema is YAML file with all configuration of the both backup and restore workflows. Lets see its minimal structure:

```sh
sbt manage create_schema
```

You opened template will look something like this:

```yaml
credentials: your-secret

targets:
- /path/to/local/folder/or/file

destination: /path/on/the/cloud
```

After credentials, targets and destination modifying, save and exit. However, *destination* path will be created automatically on the cloud.

## Backup

Now we can start backup operation with:

```sh
sbt backup your-schema-name
```

If everything was configured right, the local pack would be created and after authorization would be sent to the Google Drive.

## Restore

Uploaded backup could be simply restored with next command:

```sh
sbt --cloud cloud_google_drive --destination /path/on/the/cloud --credentials your-secret restore your-schema-name
```

The command a bit weird, but why it looks like this explained [here](). Restore workflow requires user attention by default. After archive was download and unpacked, tool will ask what to do with data. There are a few possible ways to restore:

- abort; leave local pack unpacked
- restore to */restored* folder
- try to rewrite original data; all failed targets would be placed to */restored* folder

*/restored* folder exists under tool's tmp dir:

- Windows: `%localappdata%/[COPYRIGHT]/simple-backup-tool/your-schema-name/`
- Linux: `$HOME/.local/state/[COPYRIGHT]/simple-backup-tool/your-schema-name/`

There are also contained session cache, runtime files etc. More about project's folders [here](./App%20folders.md)

## Advanced Workflows

Following topics will help to setup more complex workflows with filtering, different compression, encryption etc:

- [Automation]()
- [App folders](./App%20folders.md)
- [Backup with service account]()
- [CLI arguments]()
- [Compression]()
- [Encryption]()
- [Filtering]()
- [FAQ]()
