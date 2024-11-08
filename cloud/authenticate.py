import google.auth
import google.auth.exceptions
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import *
from miscellaneous import getTMP


def loadSecret(name:str):
    if not os.path.exists(f'./configs/secrets'):
        os.mkdir(f'./configs/secrets')
    
    secretPath = f'./configs/secrets/{name}.json'

    if not os.path.exists(secretPath):
        logger.fatal(f'failed; no OAuth2 client json file secret "{secretPath}"; get it from Google Cloud Console project')
        exit(1)

    return InstalledAppFlow.from_client_secrets_file(secretPath, SCOPES)


def getSecretName(schema) -> str:
    secretName = schema.get('secret')
    if not secretName and Config().default_secret:
        secretName = Config().default_secret
    else:
        logger.fatal(f'failed to get secret name because it not defined!')
        exit(1)
    return secretName


def authenticate(schema:dict) -> Credentials:
    logger.info('authorizing...')
    
    tmp = getTMP()
    creds:Credentials = None
    
    secretName = getSecretName(schema)
    tokenName = f'{tmp}/tokens/{secretName}.json'

    if os.path.exists(tokenName):
        if not os.path.exists(f'{tmp}/tokens/'):
            os.mkdir(f'{tmp}/tokens')
        creds = Credentials.from_authorized_user_file(tokenName, SCOPES)
    if not creds or not creds.valid:
        creds = failedGetCreds(creds, secretName)
    logger.info('success!')
    return creds


def failedGetCreds(creds:Credentials, secretName:str) -> Credentials:
    if creds and creds.expired and creds.refresh_token:
        logger.info('token expired, refreshing...')
        try:
            creds.refresh(Request())
        except google.auth.exceptions.RefreshError:
            creds = _reauthenticate(secretName)
    else:
        logger.info('getting token...')
        flow = loadSecret(secretName)
        creds = flow.run_local_server(port=0)
    saveToken(secretName, creds)
    return creds


def _reauthenticate(secretName:str) -> Credentials:
    tmp = getTMP()
    flow = loadSecret(secretName)
    creds = flow.run_local_server(port=0)

    saveToken(secretName, creds)
    
    return creds


def saveToken(secretName, creds):
    tmp = getTMP()

    if not os.path.exists(f'{tmp}/tokens/'):
        os.mkdir(f'{tmp}/tokens')
    
    with open(f'{tmp}/tokens/{secretName}.json', 'w') as token:
        token.write(creds.to_json())
