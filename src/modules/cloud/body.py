import logging

from core.context import ctx
from core.module import module_register

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import CloudModule

logger = logging.getLogger(__name__)


def entry():
    module:CloudModule = ctx.currentModule
    schema = ctx.schema
    args = ctx.args

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
    schema = ctx.schema
    args = ctx.args

    raise NotImplementedError()
