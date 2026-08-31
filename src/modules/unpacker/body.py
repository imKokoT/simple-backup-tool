import logging

from core.context import ctx
from core.module import module_register
from core.vfs import VFile

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import UnpackerModule
    from modules.cryptography import CryptographyModule

logger = logging.getLogger(__name__)


def entry():
    module:UnpackerModule = ctx.currentModule
    schema = ctx.schema
    args  = ctx.args

    logger.info('unpacking loaded pack...')
    module.packStream = s = VFile(module.packPath, 'r')

    # try decrypt pack
    c:CryptographyModule = module_register.get('cryptography')
    if c.isEncrypted(module.packPath):
        logger.info('encryption detected')
        s = c.decryptionStream(s)

    # decompress stream
    print(s.read(128))
