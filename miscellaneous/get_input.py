import os
from getpass import getpass
from typing import Literal
from properties import *


def confirm(msg:str, default:Literal['yes','no']='no') -> bool:
    '''ask yes or no to confirm'''
    ## gui input

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
    '''get folder path from user'''
    ## gui input

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
    '''safely get password'''
    ## gui input

    ## terminal input
    return getpass(f'{YC}{msg}{DC}')


def getString(msg:str) -> str:
    '''get string input'''
    ## gui input

    ## terminal input
    return input(msg)
