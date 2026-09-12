import logging

from core.module import Chain
from . import create_schema

logger = logging.getLogger(__name__)


class ManageChain(Chain):
    name = 'manage'
    description = 'Helper to manage application'
    actions = [
        'create_schema'
    ]

    def registerCommandArguments(self):
        self.subparser.add_argument(
            'action', 
            help=f'Possible values: {', '.join(self.actions)}'
        )

    def run(self, args):
        match args.action:
            case 'create_schema': create_schema.entry()
            case _:
                logger.error('wrong action')
                exit(1)
