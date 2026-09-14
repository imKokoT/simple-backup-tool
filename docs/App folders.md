# App folders

The tool stores all files in three different locations.

## Logs

Application logs are stored into root app folder under `./logs/`. Application stores last 10 sessions, that you could discover in case of errors, debugging etc.

## Configs

App configs, schemas and credentials are located under:

- Windows: `%appdata%/[COPYRIGHT]/simple-backup-tool/`
- Linux: `$HOME/.local/share/[COPYRIGHT]/simple-backup-tool`

```
simple-backup-tool/
|- config.yaml
|- config-old.yaml
|- schemas/
|   |- your-schema.yaml   
|- secrets/
    |- your-secret.cred
    |- your-secret-service.service
```

## TMP folder

Session cache, runtime files etc are located under:

- Windows: `%localappdata%/[COPYRIGHT]/simple-backup-tool/`
- Linux: `$HOME/.local/state/[COPYRIGHT]/simple-backup-tool/`

Every separate folder is a session cache. Also there is `*/**/restored` folder with potentially restored data.
