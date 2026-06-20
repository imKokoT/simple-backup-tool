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
    
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )
    
    # register modules
    module_register.register(modules.scan.ScanModule(parser))
    module_register.register(modules.cryptography.CryptographyModule(parser))
    module_register.register(modules.packer.PackerModule(parser))
    module_register.register(modules.archiver_internal.ArchiverInternalModule(parser))
    module_register.register(modules.cloud.CloudModule(parser))
    module_register.register(modules.cloud_google_drive.CloudGoogleDriveModule(parser))
    # init chains
    ctx.chains = [
        chain.BackupChain(subparsers),
        chain.RestoreChain(subparsers)
    ]

    app_config.config.load()
    args = ctx.args = parser.parse_args()
    args.func(ctx.args)
