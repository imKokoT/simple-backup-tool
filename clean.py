import os
from config import *
from miscellaneous import getTMP


def clean(fname:str):
    tmp = getTMP()
    path = os.path.join(tmp, fname)

    if os.path.basename(fname).split('.')[-1] == 'tar':
        return

    programLogger.info(f'cleaning "{path}"')
    
    if not os.path.exists(path):
        programLogger.error(f'"{path}" not exists')
        return
    
    os.remove(path)
    
