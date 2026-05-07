import shutil
import sys
from typing import Literal
from core.app_config import config


def getConfirm(expected:Literal['y','n'], msg:str='', default:Literal['y','n']='n') -> bool:
    '''Returns true if get expected confirm'''
    yn = input(f'{f'{msg}? ' if msg else 'Please confirm! '}'
               f'[{'Y/n' if default == 'y' else 'y/N'}] ')

    yn = yn.strip().lower()

    if not yn:
        return expected == default
    else:
        return yn == expected


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
