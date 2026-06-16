import modules
from chain.backup import BackupChain
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
    
    # register modules
    module_register.register(modules.scan.ScanModule(parser))
    module_register.register(modules.cryptography.CryptographyModule(parser))
    module_register.register(modules.packer.PackerModule(parser))
    module_register.register(modules.archiver_internal.ArchiverInternalModule(parser))
    module_register.register(modules.cloud.CloudModule(parser))
    # init chains
    ctx.chains = [
            BackupChain(parser)
        ]

    app_config.config.load()
    args = ctx.args = parser.parse_args()
    args.func(ctx.args)
