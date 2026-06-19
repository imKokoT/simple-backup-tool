import logging
import os
from googleapiclient.discovery import build
from httplib2 import ServerNotFoundError
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

from core.context import ctx
from .tools import authenticate, getStorageQuota
from .drive import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import CloudGoogleDriveModule

logger = logging.getLogger(__name__)


def entry():
    module:CloudGoogleDriveModule = ctx.currentModule
    schema = ctx.schema
    args = ctx.args

    os.makedirs(f'./configs/secrets', exist_ok=True)

    if module.invokeArgs['action'] == 'send':
        send()
    elif module.invokeArgs['action'] == 'download':
        ...


def send():
    module:CloudGoogleDriveModule = ctx.currentModule
    schema = ctx.schema
    args = ctx.args

    logger.info('authenticating Google Drive credentials')
    module.creds = creds = authenticate()
    
    try:
        logger.info('building service')
        module.service = build("drive", "v3", credentials=creds)

        folderId = getDestination(schema.get('destination'), None)

        cleanup(folderId)

        quota = getStorageQuota()
        logger.debug(f'storage quota: {quota}')

        logger.info('sending pack to the cloud...')
        if module.serviceCred:
            raise NotImplementedError()
        else:
            sendArchive(folderId)

        logger.info(f'archive was sent to the cloud successfully!')

    except (HttpError, RefreshError) as e:
        logger.error(f'failed to backup; error: {e}')
        exit(1)
    except ServerNotFoundError as e:
        logger.error(f'failed to backup; possibly network error: {e}')
        exit(1)
