import logging
import os

from paths import getAppDir

from .tools import openWithinEditor
from core.module import Operation
from . import schema_manage

logger = logging.getLogger(__name__)


class ManageOperation(Operation):
    name = 'manage'
    description = 'Helper to manage application'
    actions = [
        'create_schema',
        'open_schema',
        'list_schemas',

        'config',
    ]

    def registerCommandArguments(self):
        self.action_parsers = self.subparser.add_subparsers(
            dest="action",
            help=f'Possible values: {', '.join(self.actions)}',
            required=True,
        )

        # --- schema manage ---
        createSchema = self.action_parsers.add_parser('create_schema')
        createSchema.set_defaults(func=schema_manage.create)
        
        openSchema = self.action_parsers.add_parser('open_schema')
        openSchema.add_argument('schema_name')
        openSchema.set_defaults(func=schema_manage.openSchema)

        listSchemas = self.action_parsers.add_parser('list_schemas')
        listSchemas.set_defaults(func=schema_manage.listSchemas)

        # --- app config ---
        openConfig = self.action_parsers.add_parser('config')
        openConfig.set_defaults(
            func=lambda args: openWithinEditor(getAppDir() / 'config.yaml')
        )

    def run(self, args):
        os.makedirs(getAppDir() / 'schemas', exist_ok=True)
