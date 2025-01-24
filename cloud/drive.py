import io
import json
from logger import logger
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from app_config import Config
from properties import *
from miscellaneous import updateProgressBar


def sendMeta(service, folder:str, schema:dict):
    logger.info('sending backup meta...')
    stream = io.BytesIO()

    schemaName = schema['__name__']

    if schema.get('encryption'):
        data = {
            'compressFormat': schema.get('compressFormat'),
            'encryption': schema['encryption'],
            'mode': schema.get('mode'),
            'program': schema.get('program')
        }
    else:
        data = {
            'compressFormat': schema.get('compressFormat'),
            'password': schema.get('password') is not None,
            'mode': schema.get('mode'),
            'program': schema.get('program')
        }
    meta = {
        'name': f'{schemaName}.meta',
        'parents': [folder],
        'description': f'Meta made by SBT {VERSION}\n'
                       f'see https://github.com/imKokoT/simple-backup-tool'
    }
    stream.write(bytes(json.dumps(data, separators=(',',':')), 'utf-8'))
    media = MediaIoBaseUpload(stream, mimetype='application/octet-stream')

    uploadFile = service.files().create(
        body=meta,
        media_body=media, 
        fields='id'
    ).execute()


def tryGetMeta(service, folder:str, schemaName:str) -> dict|None:
    logger.info(f'getting meta...')

    query = f"'{folder}' in parents and name='{schemaName}.meta' and trashed=false"
    response = service.files().list(q=query, spaces='drive').execute()
    files = response.get('files', [])

    if not files:
        return False
    
    metaId = files[0]['id']
    request = service.files().get_media(fileId=metaId).execute()

    return json.loads(str(request,'utf-8'))


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
            updateProgressBar(status.progress() if status else None)


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
        updateProgressBar(status.progress() if status else None)


def getDestination(service, path:str, root:str|None):
    logger.info('getting destination folder')
    
    folders = path.split('/')
    folders = [e for e in folders if e != '']

    parent = root
    for folder in folders:
        parent = _getOrCreate(service, folder, parent)

    return parent


def _getOrCreate(service, folderName:str, parent=None):
    query = f"name='{folderName}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent:
        query = f"'{parent}' in parents and " + query
    
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
