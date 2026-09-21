# Backup With Service Account

> [!NOTE]
> Before we continue, firstly we must create [service account](./Create%20Google%20Service.md#Service%20account)

Beside using client credentials there is an option to create a *service account*, to automate authentication process and separate backup storage. Also this could be useful, when the system does not have possibility of authorization in browser.

Service account has few differences from user-based. As mentioned before it does not require authorization from browser, because of downloaded *private key*, so everyone who have the key **could access service account and its shared data**!

> [!IMPORTANT]
> **DO NOT** share random folders with service account. In case of compromentation, the service could access to all data in shared folders! 
>
> Good practice is to use a separate folder for this service account.

## Setup

The backups are stored in the service account, consequently to provide access to an account, **the account must share some folder with service account, providing editing privileges**. After that copy *shared folder's ID* from the link `https://drive.google.com/drive/folders/[folder id]`

Now specify this folder in the schema:
```yaml
root: folder_id
destination: '' # could be empty string
```

> [!NOTE]
> The backup is stored in service account's dedicated storage. If the backup becomes unshared, it will be deleted automatically at next backup workflow run!
