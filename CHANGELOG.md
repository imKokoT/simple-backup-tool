
## 0.13b
**important changes**:
- **MIT is good but Apache is better (*License change*)**
- fully changed project's structure
- now project become **beta**!


## 0.12a
- broke gui plugin system '-'d (#31)
- and lets brake everything else!


## 0.11a ([commit](https://github.com/imKokoT/simple-backup-tool/commit/c56a5f1b19a0944b685a96e4c4e250c5927d8a80))
added:
- copping your schema to backup (#24)

fixed:
- unpack wrong handles relative paths
- unpack folder process can't delete not empty folder 
- all target folders saves to `0`
- abort if try to dump empty folder at packing process
- wrongly unwrap `~` if targets is string
- recursive include of schemas 

other:
- added logging of critical exceptions


## 0.10a ([commit](https://github.com/imKokoT/simple-backup-tool/commit/ce227be5a867fcb9096c953e3d63174c3907177d))
added:
- packed targets dump to logs (#25)
- **experimental api to create gui plugin (#26)** 

fixed:
- deleting all old logs instead of one
- **FIXED BIG PROBLEM WITH FILTER THAT IGNORE FILES NOT IN PATTERNS**

other:
- changed where restored files dump places from tmp to logs folder
- removed max_logs config parameter
- **speedup file scanning. now ignored folders will not scanned! (#27)**


## 0.9a ([commit](https://github.com/imKokoT/simple-backup-tool/commit/89f56bc6c3a87451197154a02ee11b6c0b7a3cf1))
added:
- AES-256, ChaCha20, ChaCha20-Poly1305 encryption algorithms
- log compressed size in internal archivers

fixed:
- abort at build service process if token exists and authorization succeed
- abort if 7z can not open archive
- downloading or reading not own files or folders
- abort if no external archiver
- internal archivers unstable


## 0.8a ([commit](https://github.com/imKokoT/simple-backup-tool/commit/22b9e205291c1926baa9f663eced4cd23477d808)) 
added:
- multiline string format of schema's 'targets' param
- schema's 'targets' param git match patterns (#12)
- zpaq external archiver (#13)
- c_args and d_args schema's params of compress and decompress external additional arguments; args param deprecated 
- **custom mode with opportunity to use own archiver**

fixed:
- abort if try to unpack files to tmp folder
- restored files numeration in tmp folder
- abort if refresh token without reauthorization


## 0.7a  ([commit](https://github.com/imKokoT/simple-backup-tool/commit/18e9be75b5076aade2f05a4427ef28037c109df8))
added:
- new param 'root' to schema to define root folder id
- cleaning not shared archives of service account
- time incrementing log files
- new config 'max_logs'

fixed:
- logs
- not saves the token if first authenticated for users creds
- service not differentiate between accounts (#20) 
- ~ path handle support of targets (#18)
- default_secret worked wrong

other changes:
- removed support of schemas.yaml


## 0.6a  ([commit](https://github.com/imKokoT/simple-backup-tool/commit/5b3654221d8aec004100f9f0dc07c26b736cf39b))
added:
- include schemas with .yml extension
- loading external scheme from path; new option -sp for main scripts
- **multi-account support; now you can use multiple secrets json, which placed in configs/secrets/ folder (#6)**
- **added service account support (#5); to separate service and user-based accounts added deferent extensions '.cred' and '.service'** 
- new schema parameter 'secret' to define which secret.json you want to use 
- new config 'default_secret', which will used if 'secret' param will not defined at schema

fixed:
- some spell
- abort if schema has wrong format with unclear error (#16)
- abort if system has no web browser (#17)

other changes:
- schemas.yaml is deprecated, and support will be removed in near future


## 0.5a  ([commit](https://github.com/imKokoT/simple-backup-tool/commit/608cb2f8cfdde57ac6854e1a38f7bd7634b9961f))
added:
- .sbtignore and .gitignore include to filter (#8)
- more flexible restore settings (#9)
- opportunity to unpack to tmp/restored (#11)

fixed:
- abort if schemas.yaml not exists
- abort if bz2 not installed (#7)
- abort when unpack to not existing directory (#10)
- logger output, doc's spell, etc


## 0.4a  ([commit](https://github.com/imKokoT/simple-backup-tool/commit/98ced2a15aa84257b4d10716a32ec4b772d77cf5))
added:
- program config file
- opportunity to create schema in configs/schemas folder
- opportunity to include other schemas
- file as target
- filter for packing


## 0.3a  ([commit](https://github.com/imKokoT/simple-backup-tool/commit/ad006ee409158819b8e0b0cd00f0c6857c6884c8))
added:
- external 7z archiver support with new compress formats: 7z, gz, bz2, xz, zip, tar
- password secure for external 7z and zip
- restore without schema

fixed:
- unpack from local schema


## 0.2a  ([commit](https://github.com/imKokoT/simple-backup-tool/commit/f26ce98d8ecf5fac3fa3cab1ec0a67ff202cc943))
- added 3 internal archivers: zip, gz, bz2


## 0.1a  ([commit](https://github.com/imKokoT/simple-backup-tool/commit/390c7b30e9303c9fa2514368f9962c6d0ad495d4))
- added opportunity to make backups and restore them.
- tar without compression
- multiple folders backup
- safe restore
