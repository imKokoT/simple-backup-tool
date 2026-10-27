# App folders

The tool stores all files in three different locations.

## Logs

Application logs are stored in the root app folder under `./logs/`. The application stores the last 10 sessions by default, which you can review in case of errors, debugging, etc.

## Configs

App configs, schemas, and credentials are located under:

- Windows: `%appdata%/simple-backup-tool/`
- Linux: `$HOME/.config/simple-backup-tool/`

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

- Windows: `%localappdata%/simple-backup-tool/`
- Linux: `$HOME/.local/state/simple-backup-tool/`

Every separate folder is a session cache. Also there is `*/**/restored` folder with potentially restored data.
