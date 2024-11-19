
## 0.7a
added:
- new param 'root' to schema to define root folder id
- cleaning not shared archives of service account

fixed:
- logs
- not saves the token if first authenticated for users creds
- service not differentiate between accounts (#20) 

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
