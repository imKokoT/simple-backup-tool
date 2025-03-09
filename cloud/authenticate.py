import os
from logger import logger
import webbrowser
import google.auth
import google.auth.exceptions
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from app_config import Config
from properties import *
from miscellaneous import getTMP
from runtime_data import rtd


def loadSecret(secretName:str) -> Credentials:
    if not os.path.exists(f'./configs/secrets'):
        os.mkdir(f'./configs/secrets')
    
    schema:dict = rtd['schema']
    secretType = None
    if os.path.exists(f'./configs/secrets/{secretName}.cred'):
        secretType = 'cred'
    elif os.path.exists(f'./configs/secrets/{secretName}.service'):
        secretType = 'service'
    else:
        logger.fatal(f'failed; no json secret OAuth2 user (.cred) or service (.service) file named "{secretName}" at secrets folder; get it from Google Cloud Console project')
        exit(1)

    secretPath = f'./configs/secrets/{secretName}.{secretType}'

    if secretType == 'cred':
        schema['__secret_type__'] = 'cred'
        flow = InstalledAppFlow.from_client_secrets_file(secretPath, SCOPES)
        try:
            creds = flow.run_local_server(port=0)
        except webbrowser.Error as e:
            logger.error(f'failed to open webbrowser; error: {e}')
            creds = flow.run_local_server(port=0, open_browser=False)
        
        saveToken(secretName, creds)
        return creds
    else:
        schema['__secret_type__'] = 'service'
        return service_account.Credentials.from_service_account_file(secretPath, scopes=SCOPES)


def getSecretName() -> str:
    secretName = rtd['schema'].get('secret')
    if not secretName and Config().default_secret:
        return Config().default_secret
    else:
        if secretName:
            return secretName
        logger.fatal(f'failed to get secret name because it not defined!')
        exit(1)


def authenticate() -> Credentials:
    logger.info('authorizing...')
    
    schema:dict = rtd['schema']
    tmp = getTMP()
    creds:Credentials = None
    
    secretName = getSecretName()
    tokenPath = f'{tmp}/tokens/{secretName}.json'
    
    if not os.path.exists(f'{tmp}/tokens/'):
        os.mkdir(f'{tmp}/tokens')

    if os.path.exists(tokenPath) and os.path.exists(f'./configs/secrets/{secretName}.cred'):
        schema['__secret_type__'] = 'cred'
        creds = Credentials.from_authorized_user_file(tokenPath, SCOPES)

    if not creds or not creds.valid:
        creds = failedCreateCreds(creds, secretName, schema)
    
    logger.info('success!')
    return creds


def failedCreateCreds(creds:Credentials, secretName:str, schema:dict) -> Credentials:
    if creds and creds.expired and creds.refresh_token:
        logger.info('token expired, refreshing...')
        try:
            creds.refresh(Request())
            schema['__secret_type__'] = 'cred'
            saveToken(secretName, creds)
        except google.auth.exceptions.RefreshError:
            creds = _reauthenticate(secretName)
    else:
        logger.info('getting token...')
        creds = loadSecret(secretName)
    return creds


def _reauthenticate(secretName:str) -> Credentials:
    creds = loadSecret(secretName)
    saveToken(secretName, creds)
    
    return creds


def saveToken(secretName, creds):
    tmp = getTMP()
    
    if not os.path.exists(f'{tmp}/tokens/'):
        os.mkdir(f'{tmp}/tokens')
    
    with open(f'{tmp}/tokens/{secretName}.json', 'w') as token:
        token.write(creds.to_json())
