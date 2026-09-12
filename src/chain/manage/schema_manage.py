import os

from properties import *
from paths import getAppDir, isValid
from .tools import openWithinEditor


def create(args):
    name = None
    schemasPath = getAppDir() / 'schemas'

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

    path = schemasPath / f'{name}.yaml'

    with open(path, 'w', encoding='utf-8') as f:
        # TODO: schema template
        f.write('# template\n')
    
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
