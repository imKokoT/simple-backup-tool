import json
import logging
import os

from core.cli import getConfirm
from core.module import Chain, module_register
from core.context import ctx
from core.schema import Schema
from paths import getAppDir, getTmpDir

logger = logging.getLogger(__name__)


class BackupChain(Chain):
    name = 'backup'
    description = 'Backup chain'
    chain = [
        'scan',
        'packer',
        'cloud'
    ]
    chainKwargs = [
        {},
        {},
        {
            'action': 'send'
        }
    ]

    def registerCommandArguments(self):
        self.subparser.add_argument('schema_name', help='schema to load')
        self.subparser.add_argument('-f', '--force', action='store_true', help='force backup')

    def run(self, args):
        ctx.schema = Schema(getAppDir() / 'schemas' / f'{ctx.args.schema_name}.yaml')
        lockPath = getTmpDir() / ctx.schema.name / '.lock'
        lockData:dict
        def updateLock(path, data):
            with open(path, 'w') as f:
                json.dump(data, f)

        if lockPath.exists():
            with open(lockPath, 'r') as f:
                lockData = json.load(f)
            
            # if other chain lock detected
            if lockData.get('chain') != self.name:
                logger.warning(f'it looks like other chain({lockData["chain"]}) was not completed for some reason')
                if getConfirm('y', 'Do you what to abort [Y] or continue current chain [N]'):
                    logger.info('aborting...')
                    quit(0)
                else:
                    os.remove(lockPath)
            # if locked current chain
            else:
                logger.warning('it looks like this backup chain was not completed for some reason')

                if not getConfirm('y', 'Do you want to continue last chain [Y] or restart chain [N]'):
                    os.remove(lockPath)
            
        if not lockPath.exists():
            lockData = {
                'chain': self.name,
                'progress': {}
            }
            updateLock(lockPath, lockData)

        logger.info('started backup chain')

        try:
            for m, k in zip(self.chain, self.chainKwargs):
                if m not in lockData['progress']:
                    logger.debug(f'invoke module {m}')
                    module_register.get(m).invoke(**k)
                    lockData['progress'][m] = 'done'
                    updateLock(lockPath, lockData)
        except SystemExit as e:
            if e.code == 0:
                logger.info('backup chain aborted')
                os.remove(lockPath)
                return
            else: 
                raise

        logger.info('ended backup chain')

        if set(lockData['progress'].keys()) & set(self.chain):
            os.remove(lockPath)
