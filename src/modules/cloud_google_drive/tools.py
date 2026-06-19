import os
import logging
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials

from core.context import ctx
from paths import getAppDir, getTmpDir

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import CloudGoogleDriveModule

logger = logging.getLogger(__name__)


def authenticate() -> Credentials:
    module:CloudGoogleDriveModule = ctx.currentModule
    schema = ctx.schema
    
    secretName = schema.get('credentials')
    secretFolderPath = getAppDir() / 'secrets'

    # check cred type
    if os.path.exists(secretFolderPath / f'{secretName}.cred'):
        serviceCred = module.serviceCred = False
    elif os.path.exists(secretFolderPath / f'{secretName}.service'):
        serviceCred = module.serviceCred = True
    else:
        logger.error(f'no json secret OAuth2 user (.cred) or service (.service) file named "{secretName}"; get it from Google Cloud Console project!')
        exit(1)

    credPath = secretFolderPath / f'{secretName}.{'service' if serviceCred else 'cred'}'
    logger.info(f'authenticating {' service' if serviceCred else ''} credentials...')

    if serviceCred:
        return service_account.Credentials.from_service_account_file(
            credPath, scopes=module.SCOPES
        )
    else:
        # try to authenticate from refresh token
        creds:Credentials = None
        tokenPath = getTmpDir() / schema.name / 'token'
        if tokenPath.exists():
            creds = Credentials.from_authorized_user_file(tokenPath, module.SCOPES)
        
        # refresh token or log in again
        if not creds or not creds.valid:
            logger.debug('failed to authenticate from token')

            if creds and creds.expired and creds.refresh_token:
                logger.debug('token expired; ask for refresh...')
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credPath, module.SCOPES
                )

                try:
                    creds = flow.run_local_server(port=0)
                except webbrowser.Error as e:
                    logger.error(f'failed to open webbrowser; error: {e}')
                    creds = flow.run_local_server(port=0, open_browser=False)
                
            _saveToken(creds)
        return creds


def _saveToken(creds:Credentials):
    schema = ctx.schema

    tmp = getTmpDir() / schema.name 
    with open(tmp / 'token', 'w') as t:
        t.write(creds.to_json())

    logger.debug('saved refresh token to tmp')


def getStorageQuota() -> dict:
    module:CloudGoogleDriveModule = ctx.currentModule

    quota = module.service.about().get(fields='storageQuota').execute()['storageQuota']
    return {
        'limit': int(quota['limit']) if quota.get('limit') else None,
        'usage': int(quota['usage'])
    }
