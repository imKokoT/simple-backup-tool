import logging

from core.context import ctx
from core.module import module_register

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import CloudModule

logger = logging.getLogger(__name__)


def entry():
    module:CloudModule = ctx.currentModule

    if module.invokeArgs['action'] == 'send':
        send()
    elif module.invokeArgs['action'] == 'download':
        download()


def send():
    module:CloudModule = ctx.currentModule
    schema = ctx.schema
    args = ctx.args

    # select cloud module
    cloud = module_register.get(
        module.cloudModules[
            module.cloudModules.index(
                schema.get('cloud')
            )]
    )

    logger.info(f'Initializing sending the pack to {cloud.name}')
    cloud.invoke(action='send')


def download():
    module:CloudModule = ctx.currentModule
    args = ctx.args

    if not args.cloud:
        logger.error(f'"cloud" parameter must be provided')
        exit(1)
    if args.cloud not in module.cloudModules:
        logger.error(f'cloud "{args.cloud}" does not exists')
        exit(1)

    # select cloud module
    cloud = module_register.get(
        module.cloudModules[
            module.cloudModules.index(args.cloud)
        ]
    )

    logger.info(f'Initializing downloading of the pack from {cloud.name}')
    cloud.invoke(action='download')
