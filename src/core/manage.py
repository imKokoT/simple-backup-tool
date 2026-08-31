import modules
import chain
from core import app_config
from properties import *
from core.module import module_register
from core.context import ctx
import argparse
import logging
import sys

logger = logging.getLogger(__name__)


def parseArgs(args):
    if len(sys.argv) == 1:
        print(f'SBT v{VERSION} | Copyright {C_YEARS} {COPYRIGHT} ({LINK})')
        return
    
    ctx.parser = parser = argparse.ArgumentParser()
    ctx.subparsers = subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )
    
    # register modules
    module_register.register(modules.scan.ScanModule())
    module_register.register(modules.cryptography.CryptographyModule())
    module_register.register(modules.packer.PackerModule())
    module_register.register(modules.unpacker.UnpackerModule())
    module_register.register(modules.archiver_internal.ArchiverInternalModule())
    module_register.register(modules.cloud.CloudModule())
    module_register.register(modules.cloud_google_drive.CloudGoogleDriveModule())
    # init chains
    ctx.chains = [
        chain.BackupChain(),
        chain.RestoreChain()
    ]

    app_config.config.load()
    args = ctx.args = parser.parse_args()
    args.func(ctx.args)
