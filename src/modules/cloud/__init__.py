from core.config_registry import D
from core.module import Module
from .body import *


class CloudModule(Module):
    name = 'cloud'
    description = 'This module manages access to a cloud'

    cloudModules = [
        'cloud_google_drive'
    ]

    def entry(self):
        entry()

    def registerCommandArguments(self):
        self.argGroup.add_argument('-c', '--cloud', help='which cloud to use')
        self.argGroup.add_argument('-d', '--destination', help='folder on the cloud, where the archive placed')
        self.argGroup.add_argument('-s', '--credentials', help='credentials file')
        self.argGroup.add_argument('--locally', action='store_true', help='prevent sending/downloading backup; useful when you want to do things locally')

    def registerSchemaParams(self):
        self.schema_config_registry.register(
            name='destination',
            type=str,
            default=None,
            description='Destination on a cloud, where to send/download a pack',
            required=True
        )
        self.schema_config_registry.register(
            name='credentials',
            type=str,
            default=None,
            description='Credential file to access a cloud'
        )
        self.schema_config_registry.register(
            name='cloud',
            type=str,
            default=self.cloudModules[0],
            description=D('What cloud to use; possible values {variant}',
                          variant=', '.join(self.cloudModules)),
            validator=lambda x: x in self.cloudModules
        )

    def registerAppConfigs(self):
        self.app_config_registry.register(
            name='backup.delete_old_before_upload',
            type=bool,
            default=False,
            description='If true, old backup on a cloud will be deleted before new one would be uploaded\n' \
                        'This could be useful for large backups is uploaded to the cloud with a little space.\n' \
                        '\n ' \
                        'WARNING: as mentioned before OLD BACKUP WILL BE DELETED BEFORE NEW ONE UPLOADED, so if\n'
                        'a backup process would broken after old one was deleted, you will lost it!'
        )
