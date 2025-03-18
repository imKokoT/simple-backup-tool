"""
this script for gui plugins support to handle input and output between gui and tool threads more safe and simple 
"""
import logging
from threading import Event
from properties import EVENT_UPDATE_DELAY
from runtime_data import rtd
from logger import logger


class EventAlreadyPushedError(Exception): ...

class EventLogHandler(logging.Handler):
    def emit(self, record):
        pushEvent('log-pushed', self.format(record))


def clearEvents():
    '''clear all events from RTD'''
    rtd['events'].clear()
    logger.debug('all events cleared!')


def getEvent(name:str):
    '''if exists automatically pop last and return name or its msg if exists'''
    if name not in rtd['events'].keys():
        return None

    if len(rtd['events'][name]) > 0:
        msg = rtd['events'][name].pop(0) if rtd['events'][name][0] else name
    else:
        rtd['events'].pop(name)
    logger.debug(f'popped event "{name}"')
    return msg


def blockUntilGet(name:str):
    '''will block thread until event exist'''
    event = Event()
    msg = None
    logger.debug(f'{event} awaits for "{name}" event')
    while not msg:
        msg = getEvent(name)
        event.wait(EVENT_UPDATE_DELAY)

    return msg


def pushEvent(name:str, msg:str=None):
    '''push new event to runtime. If to push same event it will handle as LIFO at get'''
    if name not in rtd['events'].keys():
        rtd['events'][name] = [msg]
        logger.debug(f'pushed new event "{name}"')
    else:
        rtd['events'][name].append(msg)
