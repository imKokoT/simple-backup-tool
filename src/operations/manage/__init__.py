import logging
import os

from paths import getAppDir

from .tools import openWithinEditor
from core.module import Operation
from . import schema_manage
from . import launcher

logger = logging.getLogger(__name__)


class ManageOperation(Operation):
    name = 'manage'
    description = 'Helper to manage application'
    actions = [
        'install-launcher',
        'uninstall-launcher',

        'create-schema',
        'open-schema',
        'list-schemas',

        'config',
    ]

    def registerCommandArguments(self):
        os.makedirs(getAppDir() / 'schemas', exist_ok=True)

        self.action_parsers = self.subparser.add_subparsers(
            dest="action",
            help=f'Possible values: {', '.join(self.actions)}',
            required=True,
        )

        # --- schema manage ---
        createSchema = self.action_parsers.add_parser('create-schema')
        createSchema.set_defaults(func=schema_manage.create)
        
        openSchema = self.action_parsers.add_parser('open-schema')
        openSchema.add_argument('schema_name')
        openSchema.set_defaults(func=schema_manage.openSchema)

        listSchemas = self.action_parsers.add_parser('list-schemas')
        listSchemas.set_defaults(func=schema_manage.listSchemas)

        # --- app config ---
        openConfig = self.action_parsers.add_parser('config')
        openConfig.set_defaults(
            func=lambda args: openWithinEditor(getAppDir() / 'config.yaml')
        )

        # --- launcher script installation ---
        installLauncher = self.action_parsers.add_parser('install-launcher')
        installLauncher.set_defaults(func=launcher.install)

        uninstallLauncher = self.action_parsers.add_parser('uninstall-launcher')
        uninstallLauncher.set_defaults(func=launcher.uninstall)

    def run(self, args):
        ...
