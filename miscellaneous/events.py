"""
this script for gui plugins support to handle input and output between gui and tool threads more safe and simple 
"""
import logging
from threading import Event
from typing import Any
from properties import EVENT_UPDATE_DELAY
from runtime_data import rtd
from logger import logger


class EventLogHandler(logging.Handler):
    def emit(self, record):
        pushEvent('log-pushed', self.format(record))
    
    def filter(self, record:logging.LogRecord):
        excluded = getattr(record, 'excluded', None)
        return not excluded


class Null(type):
    __slots__ = ()
    '''class-stub for default message of pushed event. 
    If not to select any msg, got message will be name of this event'''

    def __str__(self):
        return 'Null message'


def clearEvents():
    '''clear all events from RTD'''
    rtd['events'].clear()
    logger.debug('all events cleared!', extra={'excluded': True})


def popEvent(name:str) -> list:
    '''will clear event by name end return its values list. 
    if not exists raises KeyError'''
    if name not in rtd['events'].keys():
        raise KeyError(f'event with "{name}" not exists!')
    
    logger.debug(f'popped event "{name}"', extra={'excluded': True})
    return rtd['events'].pop(name)


def tryPopEvent(name:str) -> list|None:
    '''same as popEvent but if not exist returns None'''
    if name not in rtd['events'].keys():
        return None
    
    return popEvent(name)


def getEvent(name:str) -> Any|None:
    '''if exists automatically pop last msg or return name if msg is None'''
    if name not in rtd['events'].keys():
        return None

    if len(rtd['events'][name]) > 1:
        msg = rtd['events'][name].pop(0)
    else:
        msg = popEvent(name)[0]
    return msg if msg != Null else name


def blockUntilGet(name:str) -> Any|None:
    '''same as getEvent, but will block thread until event exist'''
    event = Event()
    msg = None
    logger.debug(f'{event} awaits for "{name}" event', extra={'excluded': True})
    while msg is None:
        msg = getEvent(name)
        event.wait(EVENT_UPDATE_DELAY)

    return msg


def pushEvent(name:str, msg:Any=Null):
    '''push new event to runtime. If to push same event it will handle as LIFO at get'''
    if name not in rtd['events'].keys():
        rtd['events'][name] = [msg]
        logger.debug(f'pushed new event "{name}"', extra={'excluded': True})
    else:
        rtd['events'][name].append(msg)
