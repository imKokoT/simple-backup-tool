# Backup With Service Account

> [!NOTE]
> Before we continue, we must first create a [service account](./Create%20Google%20Service.md#Service%20account).

Besides using client credentials, there is an option to create a *service account* to automate the authentication process and separate backup storage. This can also be useful when the system does not have the possibility of browser-based authorization.

A service account has a few differences from a user-based account. As mentioned before, it does not require authorization via a browser because of the downloaded *private key*; therefore, anyone who has the key **could access the service account and its shared data**!

> [!IMPORTANT]
> **DO NOT** share random folders with the service account. In case of compromise, the service could access all data in the shared folders!
>
> Good practice is to use a separate folder for this service account.

## Setup

The backups are stored in the service account; consequently, to provide access, **the account must share a folder with the service account, providing editing privileges**. After that, copy the *shared folder's ID* from the link `https://drive.google.com/drive/folders/[folder id]`.

Now, specify this folder in the schema:
```yaml
root: folder_id
destination: '' # could be empty string
```

> [!NOTE]
> The backup is stored in service account's dedicated storage. If the backup becomes unshared, it will be deleted automatically at next backup workflow run!
