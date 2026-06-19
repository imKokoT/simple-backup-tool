import logging
import re
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

from core.vfs import VFile
from core.context import ctx
from core.cli import progressBar
from paths import getTmpDir
from properties import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import CloudGoogleDriveModule

logger = logging.getLogger(__name__)
ARCHIVE_PATTERN = re.compile(r'\.(meta|archive)$') # TODO: remove .meta at release
CHUNK_SIZE = 1024*1024


def getDestination(path:str, root:str|None):
    module:CloudGoogleDriveModule = ctx.currentModule
    logger.info('getting destination folder')

    service = module.service
    folders = path.split('/')
    folders = [e for e in folders if e != '']

    parent = root
    for folder in folders:
        parent = _getOrCreate(service, folder, parent)

    return parent


def _getOrCreate(service, folderName:str, parent=None):
    query = f"name='{folderName}' and mimeType='application/vnd.google-apps.folder' and trashed=false and 'me' in owners"
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


def cleanup(folderId:str):
    module:CloudGoogleDriveModule = ctx.currentModule
    service = module.service
    schemaName = ctx.schema.name
    
    logger.info('cleaning old cloud backup if exists...')
    
    query = f"'{folderId}' in parents and name='{schemaName}.archive' and trashed=false"
    response = service.files().list(q=query, spaces='drive').execute()
    files = response.get('files', [])

    if files:
        for f in files:
            file_id = f['id']
            service.files().delete(fileId=file_id).execute()


def deleteAllNotSharedServiceArchives(folderId:str = 'root'):
    '''delete all not shared archives and its meta'''
    module:CloudGoogleDriveModule = ctx.currentModule
    service = module.service

    if not module.serviceCred:
        logger.error(f'abort deletion of not shared all archives because service account key is not using!')
        return
    
    if folderId == 'root':
        logger.info('deleting not shared archives of service account storage')

    query = f"'{folderId}' in parents and trashed=false"
    response = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name, mimeType)",
    ).execute()

    items = response.get('files', [])

    for item in items:    
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            deleteAllNotSharedServiceArchives(folderId=item['id'])
        
        if re.search(ARCHIVE_PATTERN, item['name']):
            logger.debug(f"Deleting: {item['name']}[id:{item['id']}] ({item['mimeType']})")
            service.files().delete(fileId=item['id']).execute()


def sendArchive(folderId:str):
    module:CloudGoogleDriveModule = ctx.currentModule
    service = module.service

    logger.info('sending archive to the cloud')

    endName = f'{ctx.schema.name}.archive'
    vf = VFile(
        getTmpDir() / ctx.schema.name / 'pack'
    )

    meta = {
            'name': endName,
            'parents': [folderId],
            'description': f'Backup made by SBT {VERSION}\n'
                           f'see https://github.com/imKokoT/simple-backup-tool'
        }
    
    media = MediaIoBaseUpload(vf, mimetype='application/octet-stream', chunksize=CHUNK_SIZE, resumable=True)

    uploadFile = service.files().create(
        body=meta,
        media_body=media, 
        fields='id'
    )

    response = None
    while response is None:
        status, response = uploadFile.next_chunk()
        progressBar(status.progress() if status else 100)

    vf.close()


def downloadArchive(folderId:str):
    module:CloudGoogleDriveModule = ctx.currentModule
    service = module.service

    logger.info('downloading archive from cloud...')

    name = f'{ctx.schema.name}.archive'
    vf = VFile(
        getTmpDir() / ctx.schema.name / 'pack',
        'w'
    )

    query = f"'{folderId}' in parents and name='{name}' and trashed=false and 'me' in owners"
    response = service.files().list(q=query, spaces='drive').execute()
    files = response.get('files', [])

    if not files:
        logger.error(f'failed to download "{name}" from folder {folderId}, because it does not exist')
        raise FileNotFoundError(f'failed to download "{name}" from folder {folderId}, because it does not exist')

    backup_id = files[0]['id']
    request = service.files().get_media(fileId=backup_id)

    downloader = MediaIoBaseDownload(vf, request, chunksize=CHUNK_SIZE)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        progressBar(status.progress() if status else 100, done)

    vf.close()
