import os
from getpass import getpass
from typing import Literal
from miscellaneous.events import *
from properties import *
from runtime_data import rtd


def confirm(msg:str, default:Literal['yes','no']='no') -> bool:
    '''ask yes or no to confirm
    ### events
    if gui enabled:
    - push *get-confirm*(str msg)
    - get *send-confirm*(str 'y' or 'n')'''
    ## gui input
    if rtd['gui']:
        pushEvent('get-confirm', msg)
        yn = blockUntilGet('send-confirm')
        return yn == 'y'

    ## terminal input
    yn = input(f'{YC}{msg} [{'y/N' if default == 'no' else 'Y/n'}]{DC}').lower().strip()   
    if yn in ('y', 'yes'):
        return True
    elif yn in ('n', 'no'):
        return False
    elif default == 'no':
        return False
    elif default == 'yes':
        return True
    else:
        raise ValueError('Wrong default value!')


def getFolderPath(skip:bool=True) -> str|None:
    '''get folder path from user
    ### events
    if gui enabled:
    - push *get-folder_path*
    - push *get-folder_path-skippable*
    - get *send-folder_path*(str|None)'''
    ## gui input
    if rtd['gui']:
        if skip:
            pushEvent('get-folder_path-skippable')
        else:
            pushEvent('get-folder_path')
        path = blockUntilGet('send-folder_path')
        return path if path else None

    ## terminal input
    newPath = ''
    while not os.path.exists(newPath) or not os.path.isdir(newPath):
        newPath = input(f'Enter directory path{' or nothing to skip' if skip else ''}: ')
        if newPath.strip() == '' and skip:
            return
        if not os.path.exists(newPath) or not os.path.isdir(newPath):
            print(f'{RC}invalid path "{newPath}"!')

    return newPath


def getPassword(msg:str) -> str:
    '''safely get password
    ### events
    if gui enabled:
    - push *get-password*(str msg)
    - get *send-password*(str)'''
    ## gui input
    if rtd['gui']:
        pushEvent('get-password', msg)
        return blockUntilGet('send-password')

    ## terminal input
    return getpass(f'{YC}{msg}{DC}')


def getString(msg:str) -> str:
    '''get string input
    ### events
    if gui enabled:
    - push *get-string*(str msg)
    - get *send-string*(str)'''
    ## gui input
    if rtd['gui']:
        pushEvent('get-string', msg)
        return blockUntilGet('send-string')

    ## terminal input
    return input(msg)
