# Simple backup tool
for making backups to your Google Drive cloud by imKokoT.

# How to setup
All application configurations placed in "configs" folder.

## Requirements
- Python 3.12+
- ```pip install colorama colorlog pyyaml google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client```
- (*optionally*) [7z](https://7-zip.org/) - for faster compression and more flexibility

## Creating Google service
Before you start to configure application, firstly you must to create Google application service in [Google Console](https://console.cloud.google.com/) to get access to your Drive. **Don't worry it's free**. 
1. Firstly you must to create new project by [following this link](https://console.cloud.google.com/projectcreate).
2. Attach **Google Drive API** support by [following this link](https://console.cloud.google.com/apis/library/drive.googleapis.com).
3. Create OAuth2 credentials by [following this link](https://console.cloud.google.com/apis/credentials) and clicking on *CREATE CREDENTIALS*. Also you must *configure consent screen* if you have not.
4. Download client secrets json file and place it to configs folder and rename to *client-secrets.json*

## Configure backup schema
When you have finished with creds, now you can create your first backup. SBT use *schemas.yaml* file to save all backup schemas and its configurations. Create *schemas.yaml* in configs folder and place next template:
```yaml
# to define new schema use any name
new-schema:
  compressFormat: tar # 7z, gz, bz, zip; null or ignored is tar
  compressLevel: 5 # don't work with tar; default is 5; can be ignored
  password: null # only 7z & zip; can be ignored
  # internal only for gz
  # external will try to use external program
  mode: external
  destination: 'test/folder/in/your/drive' # google disk backup folder path
  # local folders to backup
  folders: [
    'path/to/your/local/folder'
  ]
```
You can backup several folders at once. Backup will be placed in *destination* path. Don't worry, program will create all necessary folders in Drive! Also, it's not necessary, but recommended to use same destination for your backups, because SBT will duplicate configs for your backups.

## Create first backup
SBT has two main scripts: *backup.py* and *restore.py*. To backup run
```sh
python backup.py <your schema name>
```
Or to get docs:
```sh
python backup.py
```
If you have done all right, backup will created successfully.

## Restore your data
To restore simply run
```sh
python restore.py <your schema name>
```
And backup will be restored to local paths, which you select before creating backup. Restore process WILL NOT delete or change all current files BUT will replace or insert all that contains in backup. 
**WARNING: if local path not exits unpack of this folder will fail, but your downloaded data will placed in *tmp* local program folder in TAR archive *your schema name.tar***