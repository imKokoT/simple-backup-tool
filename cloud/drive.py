import io
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from config import *
from miscellaneous import updateProgressBar


def send(service, fpath:str, endName:str, folder=None):
    '''
    @param fpath: path to target file
    @param endName: name of file, which will be in cloud
    @param folder: folder where will place the file 

    Send file to cloud
    '''
    meta = {
            'name': endName,
            'parents': [folder],
            'description': f'Backup made by SBT {VERSION}\n'
                           f'see https://github.com/imKokoT/simple-backup-tool'
        }
    with open(fpath, 'rb') as f:
        media = MediaIoBaseUpload(f, mimetype='application/octet-stream', chunksize=Config().download_chunk_size, resumable=True)

        uploadFile = service.files().create(
            body=meta,
            media_body=media, 
            fields='id'
            )

        response = None
        while response is None:
            status, response = uploadFile.next_chunk()
            if status:
                updateProgressBar(status.progress())
        updateProgressBar(1)
        print()


def download(service, fpath:str, name:str, folder:str):
    '''
    @param fpath: path, where to save the file
    @param name: file name in cloud
    @param folder: folder where will place the file 
    '''
    logger.info(f'downloading {name} from cloud...')
    query = f"'{folder}' in parents and name='{name}' and trashed=false"
    response = service.files().list(q=query, spaces='drive').execute()
    files = response.get('files', [])

    if not files:
        logger.error(f'failed to download "{name}" from folder {folder}, because it does not exist')
        raise FileNotFoundError(f'failed to download "{name}" from folder {folder}, because it does not exist')

    backup_id = files[0]['id']
    request = service.files().get_media(fileId=backup_id)
    fh = io.FileIO(fpath, 'wb')

    downloader = MediaIoBaseDownload(fh, request, chunksize=Config().download_chunk_size)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        updateProgressBar(status.progress())
    updateProgressBar(1)
    print()


def getDestination(service, path:str, root:str|None):
    logger.info('getting destination folder')
    
    folders = path.split('/')
    folders = [e for e in folders if e != '']

    for folder in folders:
        parent = _getOrCreate(service, folder, root)

    return parent


def _getOrCreate(service, folderName:str, parent=None):
    if parent:
        query = f"'{parent}' in parents and name='{folderName}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    else:
        query = f"name='{folderName}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    
    response = service.files().list(q=query, spaces='drive').execute()
    files = response.get('files', [])

    if files:
        return files[0]['id']
    else:
        meta = {
            'name': folderName,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent:
            meta['parents'] = [parent]

        folder = service.files().create(body=meta, fields='id').execute()
        return folder['id']
