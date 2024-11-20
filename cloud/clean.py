import re
from logger import logger
from properties import *


def cleanup(service, folder:str, schemaName:str):
    logger.info('cleaning old cloud backup if exists...')

    query = f"'{folder}' in parents and (name='{schemaName}.archive' or name='{schemaName}.meta') and trashed=false"
    response = service.files().list(q=query, spaces='drive').execute()
    files = response.get('files', [])

    if files:
        for f in files:
            file_id = f['id']
            service.files().delete(fileId=file_id).execute()


def deleteAllNotSharedServiceArchives(service, schema:dict):
    '''delete all not shared archives and its meta'''
    folderId = 'root'
    p = re.compile(r'\.(meta|archive)$')

    if schema['__secret_type__'] != 'service':
        logger.error(f'abort deletion of not shared all archives because service account key is not using!')
        return

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
            deleteAllNotSharedServiceArchives(service, folder_id=item['id'])
        
        if re.search(p, item['name']):
            logger.debug(f"Deleting: {item['name']}[id:{item['id']}] ({item['mimeType']})")
            service.files().delete(fileId=item['id']).execute()
