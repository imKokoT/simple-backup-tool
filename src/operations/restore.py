import json
import logging
import os

from core.app_config import config
from core.cli import getConfirm
from core.module import Operation, module_register
from core.context import ctx
from core.schema import Schema
from paths import getAppDir, getTmpDir

logger = logging.getLogger(__name__)


class RestoreOperation(Operation):
    name = 'restore'
    description = 'Restore backup from cloud'
    workflow = [
        'cloud',
        'unpacker'
    ]
    modulesKwargs = [
        {'action': 'download'},
        {}
    ]

    def registerCommandArguments(self):
        self.subparser.add_argument('schema_name', help='schema to load')
        self.subparser.add_argument('-f', '--force', action='store_true', help='force restore')

    def run(self, args):
        os.makedirs(getTmpDir() / args.schema_name, exist_ok=True)
        schema = ctx.schema = Schema(getAppDir() / 'schemas' / f'{ctx.args.schema_name}.yaml', tryLoad=True)
        lockPath = getTmpDir() / args.schema_name / '.lock'
        lockData:dict
        
        def updateLock(path, data):
            with open(path, 'w') as f:
                json.dump(data, f)

        # override app config
        if schema.get('app_config_override'):
            config.override(schema.get('app_config_override'))

        if lockPath.exists():
            with open(lockPath, 'r') as f:
                lockData = json.load(f)
            
            # if other workflow lock detected
            if lockData.get('workflow') != self.name:
                logger.warning(f'it looks like other workflow({lockData["workflow"]}) was not completed for some reason')
                if getConfirm('y', 'Do you what to abort [Y] or continue current workflow [N]'):
                    logger.info('aborting...')
                    quit(0)
                else:
                    os.remove(lockPath)
            # if locked current workflow
            else:
                logger.warning('it looks like this restore workflow was not completed for some reason')

                if not getConfirm('y', 'Do you want to continue last workflow [Y] or restart workflow [N]'):
                    os.remove(lockPath)
            
        if not lockPath.exists():
            lockData = {
                'workflow': self.name,
                'progress': {}
            }
            updateLock(lockPath, lockData)

        logger.info('started restore workflow')

        try:
            for m, k in zip(self.workflow, self.modulesKwargs):
                if m not in lockData['progress']:
                    logger.debug(f'invoke module {m}')
                    module_register.get(m).invoke(**k)
                    lockData['progress'][m] = 'done'
                    updateLock(lockPath, lockData)
        except SystemExit as e:
            if e.code == 0:
                logger.info('backup workflow aborted')
                os.remove(lockPath)
                return
            else: 
                raise

        logger.info('ended restore workflow')

        if set(lockData['progress'].keys()) & set(self.workflow):
            os.remove(lockPath)
