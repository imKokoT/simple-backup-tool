"""
this script for gui plugins support to handle input and output between gui and tool threads more safe and simple 
"""
from threading import Event
from properties import EVENT_UPDATE_DELAY
from runtime_data import rtd
from logger import logger


class EventAlreadyPushedError(Exception): ...


def get_event(name:str):
    '''if exists automatically pop it and return name or its msg if exists'''
    if name not in rtd['events'].keys():
        return None

    msg = rtd['events'][name] if rtd['events'][name] else name
    rtd['events'].pop(name)
    logger.debug(f'popped event {name}')
    return msg


def blockUntilGet(name:str):
    '''will block thread until event exist and pop'''
    event = Event()
    msg = None
    logger.debug(f'{event} awaits for "{name}" event')
    while not msg:
        msg = get_event(name)
        event.wait(EVENT_UPDATE_DELAY)

    return msg


def push_event(name:str, msg:str=None):
    '''push new event to runtime'''
    if name not in rtd['events'].keys():
        rtd['events'][name] = msg
        logger.debug(f'pushed event "{name}"')
    else:
        raise EventAlreadyPushedError(f'event {name} already exists!')
