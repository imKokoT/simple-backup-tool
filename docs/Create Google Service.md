# Creating Google Service

> [!NOTE]
> See [App folders topic](./App%20folders.md) to discover where data folders are located.

Before starting to configure the application, we must first create a Google application service in the [Google Console](https://console.cloud.google.com/) to gain access to our Drive. **Don't worry, it's free**.

1. Firstly, you must create a new project by [following this link](https://console.cloud.google.com/projectcreate).
2. Enable **Google Drive API** support by [following this link](https://console.cloud.google.com/apis/library/drive.googleapis.com).

SBT supports two types of accounts: user-based and service accounts.

## User-based

An OAuth2 account requires authorization via a browser to confirm access. It is more suited for personal usage. It also needs regular token refreshing; however, usually, a single verification is enough.

1. Create OAuth2 client credentials by [following this link](https://console.cloud.google.com/apis/credentials), clicking on *CREATE CREDENTIALS*, and selecting *OAuth Client ID*. You must also *configure the consent screen* if you have not already done so.
2. Download the client secrets JSON file, place it in the `/secrets/` folder, and rename it to *your-secret.cred*

## Service account

A service account is permanent, and anyone who has a key can access your backups. It is intended for fully automated, headless usage. Backups are stored in the service account's Drive storage. This means your personal Drive space will not be affected, BUT the service account has the same quota as any gmail.com account (a 15GB limit).

> [!NOTE]
> A service account has a default storage limit of 15GB, BUT this does not mean that you cannot buy more space. Unfortunately, it is a slightly more complex task than buying more space for a personal account.

1. Create a service account by [following this link](https://console.cloud.google.com/apis/credentials), clicking on *CREATE CREDENTIALS*, and selecting *Service account*. You must also *configure the consent screen* if you have not already done so.
2. Access your service account settings by [following this link](https://console.cloud.google.com/iam-admin/serviceaccounts), selecting *your service*, going to the *Keys* tab, and clicking *Manage keys*.
3. Create a new key in the *Keys* tab by clicking *ADD KEY* -> *Create new key* -> *JSON*. Your key will be created and downloaded. Place it in the `secrets/` folder and rename it to *your-secret-service.service*
4. Share your folder with your service account with the *Editor* role and save the folder's ID. You can directly copy the folder's ID from its link after `https://drive.google.com/drive/u/0/folders/`.

> [!WARNING]
> The tool distinguishes between user-based and service credentials by file extension: *.cred* and *.service* respectively!
