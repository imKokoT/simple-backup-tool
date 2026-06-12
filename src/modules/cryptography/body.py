import logging
from core.context import ctx

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import CryptographyModule

logger = logging.getLogger(__name__)


def entry():
    module:CryptographyModule = ctx.currentModule
    schema = ctx.schema
    args = ctx.args
