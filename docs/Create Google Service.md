# Creating Google Service

> [!NOTE]
> See [App folders topic](./App%20folders.md) to discover where data folders are located

Before starting to configure the application, firstly we must to create Google application service in [Google Console](https://console.cloud.google.com/) to get access to our Drive. **Don't worry it's free**.

1. Firstly you must to create new project by [following this link](https://console.cloud.google.com/projectcreate).
2. Attach **Google Drive API** support by [following this link](https://console.cloud.google.com/apis/library/drive.googleapis.com).

SBT supports two types of accounts: user-based and service account. 

## User-based

OAuth2 account requires authorization via browser to confirm access. It is more about personal usage. It also needs to regular refresh a token. However, usually it's enough of a single verification.

1. Create OAuth2 client credentials by [following this link](https://console.cloud.google.com/apis/credentials) and clicking on *CREATE CREDENTIALS* and on *OAuth Client ID*. Also you must *configure consent screen* if you have not.
2. Download client secrets json file and place it to `/secrets/` folder, and rename to *your-secret.cred*

## Service account

Is permanent and everyone, who has a key can access your backups. It is more about fully automated headless usage. Also backups are stored in a service account's Drive storage. This means that your Drive space will not be affected, BUT the service account has same quota, like any gmail.com accounts with a 15GB limit.

> [!Note]
> Service account has default storage limit within 15GB, BUT it does not mean that you can't buy more space. Unfortunately it is slightly complex task than buy more space for personal account.

1. Create OAuth2 service account by [following this link](https://console.cloud.google.com/apis/credentials) and clicking on *CREATE CREDENTIALS* and on *Service account*. Also you must *configure consent screen* if you have not.
2. Access your service account settings by [following this link](https://console.cloud.google.com/iam-admin/serviceaccounts) and selecting *your service* -> *Actions* tab -> *Manage keys*.
3. Create new key at tab *Keys* and click on *ADD KEY* -> *Create new key* -> *Json*. Your key will be created and downloaded. Place it to `secrets/` folder and rename to *your-secret-service.service*
4. Share your folder for your service account with role *Editor* and save folder's id. You can directly copy folder's id from its link after `https://drive.google.com/drive/u/0/folders/`.

> [!WARNING]
> Tool distinguishes user-based and service creds by file extension - *.cred* and *.service* respectively!
