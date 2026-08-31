import logging

from core.context import ctx
from core.module import module_register

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import UnpackerModule

logger = logging.getLogger(__name__)


def entry():
    module:UnpackerModule = ctx.currentModule
    schema = ctx.schema
    args  = ctx.args
