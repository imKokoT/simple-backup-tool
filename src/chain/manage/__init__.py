import logging

from core.module import Chain
from . import schema_manage

logger = logging.getLogger(__name__)


class ManageChain(Chain):
    name = 'manage'
    description = 'Helper to manage application'
    actions = [
        'create_schema',
        'open_schema',
    ]

    def registerCommandArguments(self):
        self.action_parsers = self.subparser.add_subparsers(
            dest="action",
            help=f'Possible values: {', '.join(self.actions)}',
            required=True,
        )

        createSchema = self.action_parsers.add_parser('create_schema')
        createSchema.set_defaults(func=schema_manage.create)
        
        openSchema = self.action_parsers.add_parser('open_schema')
        openSchema.add_argument('schema_name')
        openSchema.set_defaults(func=schema_manage.openSchema)

    def run(self, args):
        ...
