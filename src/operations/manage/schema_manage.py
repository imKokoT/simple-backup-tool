import os
import secrets
import string

from core.cli import getConfirm, getOption
from core.schema import Schema, schema_config_registry
from properties import *
from core.paths import getAppDir, isValid
from .tools import openWithinEditor


def create(args):
    name = None
    schemasPath = getAppDir() / 'schemas'
    dumpSettings = {}

    # get name
    while not name:
        name = input('Enter schema name: ')

        if os.path.exists(schemasPath / f'{name}.yaml'):
            print(f'{RC}This name is already used{DC}')
            name = None
            continue
        if not isValid(schemasPath / f'{name}.yaml'):
            print(f'{RC}Invalid name{DC}')
            name = None
            continue

    # ask for disable comments
    if getConfirm('y',  'Disable comments'):
        dumpSettings['disable_comments'] = True


    path = schemasPath / f'{name}.yaml'
    
    # minimal settings
    schema = Schema(path, True)

    # ask for template
    match getOption(
        [
            'minimal',
            'standard',
            'empty',
            'full'
        ],
        'Select template type',
        default=2
    ):
        case 1: # minimal
            schema.set('include', ['schema-name1', 'schema-name2'])
            schema.set('credentials', 'your-secret')
            schema.set('targets', ['/path/to/folder/'])
            schema.set('destination', '/path/in/the/cloud')

        case 2: # standard
            schema.set('include', ['schema-name1', 'schema-name2'])
            schema.set('credentials', 'your-secret')

            schema.set('packer.level', schema_config_registry.get('packer.level').default)
            schema.set('packer.format', schema_config_registry.get('packer.format').default)

            schema.set('encryption', 'aes')
            schema.set('password', ''.join(
                    [secrets.choice(string.ascii_letters + string.digits + string.punctuation) 
                     for _ in range(24)]
                )
            )

            schema.set('targets', ['/path/to/folder/'])
            schema.set('destination', '/path/in/the/cloud')
        
        case 3: # empty
            schema.set('include', ['schema-name1', 'schema-name2'])
        
        case 4: # full
            for k in schema_config_registry.all():
                schema._values[k.name] = k.default
    
    schema.dump(**dumpSettings)

    # try open schema to edit
    openWithinEditor(path)

    print(f'{GC}successfully created template {path}{DC}')


def openSchema(args):
    path = getAppDir() / 'schemas' / f'{args.schema_name}.yaml'

    if not path.exists():
        print(f'{RC}Schema does not exists!{DC}')
    
    openWithinEditor(path)


def listSchemas(args):
    schemasPath = getAppDir() / 'schemas'

    schemas = [os.path.basename(f) for f in os.listdir(schemasPath) 
             if os.path.isfile(os.path.join(schemasPath, f)) and
                f.endswith('.yaml')]
    
    for f in schemas:
        print(f' - {LGC}{f}{DC}')
