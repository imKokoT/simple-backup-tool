import os
import subprocess
import sys

from properties import *
from paths import getAppDir, isValid


def entry():
    name = None
    schemasPath = getAppDir() / 'schemas'

    # get name
    while not name:
        name = input('Enter schema name: ')

        if os.path.exists(schemasPath / f'{name}.yaml'):
            print(f'{RC}This name is already used{DC}')
            name = None
            continue
        if not isValid(f'{name}.yaml'):
            print(f'{RC}Invalid name{DC}')
            name = None
            continue

    path = schemasPath / f'{name}.yaml'

    with open(path, 'w', encoding='utf-8') as f:
        f.write('# template\n')
    
    # try open schema to edit
    if sys.platform == 'win32':
        os.startfile(path)
    elif sys.platform == 'linux':
        subprocess.run(["xdg-open", path], check=False)

    print(f'{GC}successfully created template {path}{DC}')
