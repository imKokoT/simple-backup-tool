import os
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
import google.auth
from config import *
from tools import updateProgressBar


def authenticate() -> Credentials:
    programLogger.info('authorizing...')
    creds = None
    if not os.path.exists('./configs/client-secrets.json'):
        programLogger.error('failed; no OAuth2 client json file secrets "./configs/client-secrets.json"; get it from Google Cloud Console project')
        exit(1)

    if os.path.exists('./configs/token.json'):
        creds = Credentials.from_authorized_user_file('./configs/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            programLogger.info('token expired, refreshing...')
            try:
                creds.refresh(Request())
            except google.auth.exceptions.RefreshError:
                creds = _reauthenticate()
        else:
            programLogger.info('getting token...')
            flow = InstalledAppFlow.from_client_secrets_file('./configs/client-secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('./configs/token.json', 'w') as token:
            token.write(creds.to_json())
    programLogger.info('success!')
    return creds


def _reauthenticate():
    flow = InstalledAppFlow.from_client_secrets_file('./configs/client-secrets.json', SCOPES)
    creds = flow.run_local_server(port=0)

    with open('./configs/token.json', 'w') as token:
        token.write(creds.to_json())
    
    return creds


def send(service, fpath:str, endName:str, folder=None):
    '''
    @param fpath: path to target file
    @param endName: name of file, which will be in cloud
    @param folder: folder where will place the file 

    Send file to cloud
    '''
    meta = {
            'name': endName,
            'parents': [folder]
        }
    with open(fpath, 'rb') as f:
        media = MediaIoBaseUpload(f, mimetype='application/octet-stream', chunksize=DOWNLOAD_CHUNK_SIZE, resumable=True)

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
        print()

def download(service, fpath:str, name:str, folder):
    '''
    @param fpath: path, where to save the file
    @param name: file name in cloud
    @param folder: folder where will place the file 
    '''
    programLogger.info(f'downloading {name} from cloud...')
    query = f"'{folder}' in parents and name='{name}' and trashed=false"
    response = service.files().list(q=query, spaces='drive').execute()
    files = response.get('files', [])

    if not files:
        programLogger.error(f'failed to download "{name}" from folder {folder}, because it does not exist')
        raise FileNotFoundError(f'failed to download "{name}" from folder {folder}, because it does not exist')

    backup_id = files[0]['id']
    request = service.files().get_media(fileId=backup_id)
    fh = io.FileIO(fpath, 'wb')

    downloader = MediaIoBaseDownload(fh, request, chunksize=DOWNLOAD_CHUNK_SIZE)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        updateProgressBar(status.progress())
    print()


def getDestination(service, path:str):
    programLogger.info('getting destination folder')
    
    folders = path.split('/')
    folders = [e for e in folders if e != '']

    parent = None  # Start with the root folder

    for folder in folders:
        parent = _getOrCreate(service, folder, parent)

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