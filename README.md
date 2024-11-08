# Simple backup tool
for making backups to your Google Drive cloud by imKokoT.

# How to setup
All application configurations placed in "configs" folder.

## Requirements
- supported systems: Windows, Linux
- Python 3.12+
- ```pip install colorama colorlog pyyaml pathspec google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client```
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
  secret: main # secret.json from secrets folder; can be ignored if in config.yml has defined default secret
  # include others schema values
  # you can override params that you have included
  include: include
  destination: 'test/folder/in/your/drive' # google disk backup folder path
  # list of all ignored files or folders; similar to .gitignore functionality
  # works for target folders, files always required
  ignore: |
    *.log
    cache/
  # local folders or files to backup
  targets: [
    'path/to/your/local/folder',
    'path/to/your/local/file'
  ]

include:
  compressFormat: 7z # 7z, gz, bz2, zip, xz; null or ignored is tar
  compressLevel: 5 # don't work with tar; default is 5; can be ignored
  password: null # only external 7z & zip; can be ignored
  # internal only for gz, bz2, zip
  # external will try to use external program
  mode: external
  program: 7z # now supports only 7z; only external
  args: [] # only external; additional command line arguments at compress process; can be ignored
```
You can backup several folders at once. Backup will be placed in *destination* path. Don't worry, program will create all necessary folders in Drive!

Also you can create schemas in */configs/schemas/* folder. Create a new file with name *your-schema.yaml* and add
```yaml
secret: main
compressFormat: bz2
compressLevel: 9
mode: internal

destination: 'test/folder/in/your/drive'
targets: [
  'path/to/your/local/folder',
  'path/to/your/local/file'
]
```

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
**WARNING: if local path not exits unpack of this folder will fail, but your downloaded data will placed in *tmp* local program folder in TAR archive *your schema name.tar***.
Also *restore.py* has additional options, see help with `python restore.py -h` option.

# config.yaml
Application settings contains at *config.yaml* from configs folder. You can change settings to control this tool.
### cloud configs
 - *default_secret* - default secret, which will used if 'secret' param will not defined at schema  
 - *download_chunk_size* - Google Drive download chunk size; default 10MB
### packer's configs
 - *allow_local_replace* - if true, restored backup will rewrite current local changes, if false will create new folder
 - *ask_before_replace* - if true, will ask before replace files
 - *ask_for_other_extract_path* - if true, will ask for path if failed to unpack folder or file
 - *include_gitignore* - if true, will include .gitignore files patterns
 - *restore_to_tmp_if_path_invalid* - if true, will restore target folder or file to tmp/restored
### miscellaneous
 - *auto_remove_archive* - if true, archives, that was created or downloaded, will be deleted; .tar excluded
 - *hide_password_len* - if true, will hide length of password at encryption process; if false password will hide with \*
 - *human_sizes* - if true, byte sizes will print in "B", "KB", "MB", "GB", "TB"

# Advanced ignore settings
Schema's *ignore* parameter will ignore global and always. But if you don't want to write vary large ignore patterns in schema, you can create *.sbtignore* file at some place in target directory. *.sbtignore* includes *.gitignore* syntax.

Beside this, you can include *.gitignore* files too, BUT you should to enable this function by setting *include_gitignore* to **true** at the app config.
