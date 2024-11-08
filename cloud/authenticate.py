import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import *


def authenticate() -> Credentials:
    logger.info('authorizing...')
    creds:Credentials = None
    if not os.path.exists('./configs/client-secrets.json'):
        logger.error('failed; no OAuth2 client json file secrets "./configs/client-secrets.json"; get it from Google Cloud Console project')
        exit(1)

    if os.path.exists('./configs/token.json'):
        creds = Credentials.from_authorized_user_file('./configs/token.json', SCOPES)
    if not creds or not creds.valid:
        creds = failedGetCreds(creds)
    logger.info('success!')
    return creds


def failedGetCreds(creds:Credentials) -> Credentials:
    if creds and creds.expired and creds.refresh_token:
        logger.info('token expired, refreshing...')
        try:
            creds.refresh(Request())
        except google.auth.exceptions.RefreshError:
            creds = _reauthenticate()
    else:
        logger.info('getting token...')
        flow = InstalledAppFlow.from_client_secrets_file('./configs/client-secrets.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('./configs/token.json', 'w') as token:
        token.write(creds.to_json())
    return creds


def _reauthenticate() -> Credentials:
    flow = InstalledAppFlow.from_client_secrets_file('./configs/client-secrets.json', SCOPES)
    creds = flow.run_local_server(port=0)

    with open('./configs/token.json', 'w') as token:
        token.write(creds.to_json())
    
    return creds
