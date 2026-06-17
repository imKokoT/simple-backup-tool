import logging
import os

from core.context import ctx

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

    logger.info('authorizing Google Drive credentials')
