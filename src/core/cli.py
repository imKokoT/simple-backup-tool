from getpass import getpass
import shutil
import sys
from typing import Literal
from core.app_config import config
from properties import *


def getConfirm(expected:Literal['y','n'], msg:str='', default:Literal['y','n']='n') -> bool:
    '''Returns true if get expected confirm'''
    yn = input(f'{f'{msg}? ' if msg else 'Please confirm! '}'
               f'[{'Y/n' if default == 'y' else 'y/N'}] ')

    yn = yn.strip().lower()

    if not yn:
        return expected == default
    else:
        return yn == expected


def getOption(options:list[str], msg:str='Please select an option', default:int=None) -> int:
    '''Asks user to select 1, 2, 3... options and returns the index (1-based)'''
    print(f'\n{msg}:')
    for i, option in enumerate(options, 1):
        suffix = ' (default)' if default == i else ''
        print(f'{i}) {option}{suffix}')

    while True:
        prompt = f'Select [1-{len(options)}]'
        if default is not None:
            prompt += f' (default: {default})'
        prompt += ': '

        choice = input(prompt).strip()

        if not choice and default is not None:
            return default

        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(options):
                return idx
        print(f'{RC}Invalid selection. Please enter a number between 1 and {len(options)}.{DC}')


def iprint(*strings):
    '''Inline print'''
    sys.stdout.write(f'\r{' '.join(strings)}')
    sys.stdout.flush()


def progressBar(unit:float, end:bool=False, ppu:float=1.0):
    '''
    Print progress bar

    If end is True, progress bar will finish with 100% and print newline

    `ppu` is percents per unit 
    '''
    progress = (ppu / 100) * unit if unit else 0.0
    progress = 1 if progress > 1 else progress

    bar_length = shutil.get_terminal_size().columns - 8
    blocks = int(progress * bar_length)
    progress_bar_text = "█" * blocks + "░" * (bar_length - blocks)
    
    sys.stdout.write(f"\r  {int(progress * 100)}%  {progress_bar_text}")
    sys.stdout.flush()

    if end:
        progressBar(unit=1)
        return
    if progress >= 1:
        print()


def humanSize(sizeBytes:int) -> str:
    '''returns formatted size as string in B,KB,MB and etc'''
    if not config.get('appearance.human_sizes'):
        return f'{sizeBytes}B'
    if sizeBytes == 0:
        return '0B'
    size_units = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')
    unit_index = int((len(str(sizeBytes)) - 1) / 3)
    readable_size = sizeBytes / (1024 ** unit_index)
    return f"{readable_size:.2f}{size_units[unit_index]}"


def getSecret(msg:str) -> str:
    return getpass(msg)
