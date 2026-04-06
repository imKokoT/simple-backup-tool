from core.app_config import config
from core.context import ctx
from paths import getTmpDir

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from modules.scan import ScanModule


def scan():
    module:ScanModule = ctx.currentModule
    schema = ctx.schema
    args = ctx.args

    ignore = schema.get('ignore')
    targets = schema.get('targets')

    tmpDir = getTmpDir() / schema.name
    tmpDir.mkdir(parents=True, exist_ok=True)

