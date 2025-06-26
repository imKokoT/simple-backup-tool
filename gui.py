#!/usr/bin/env python3
import logging
import importlib
from threading import Event, Thread
from logger import logger, BASE_LOGGING_FORMAT
from properties import *
from runtime_data import rtd
from miscellaneous.events import EventLogHandler
from miscellaneous.miscellaneous import catchCritical


def _eventHandler():
    event = Event()

    while True:
        # events...
        event.wait(EVENT_UPDATE_DELAY)

@catchCritical
def _start():
    logger.info('stating gui...')
    rtd['gui'] = True
    rtd['events'] = {}
    eventHandlerThread = Thread(target=_eventHandler, daemon=True)
    guiThread:Thread = None

    logger.info('importing gui plugin')
    try:
        guiModule = importlib.import_module('plugins.gui.main')
        start_gui = getattr(guiModule, 'start_gui', None)
        guiThread = Thread(target=start_gui, daemon=True)
    except ModuleNotFoundError as e:
        logger.fatal(f'failed to import gui plugin from plugins folder! error: {e}')
        exit(1)
    except Exception as e:
        logger.fatal(f'importing of gui plugin interrupted with error: {e}')
        exit(1)
    
    eventHandlerThread.start()
    
    # add new logger handler to push logs as events
    handler = EventLogHandler()
    handler.setFormatter(logging.Formatter(BASE_LOGGING_FORMAT))
    logger.addHandler(handler)

    logger.info('starting gui thread')
    try:
        guiThread.start()
    except Exception as e:
        logger.fatal(f'starting gui plugin interrupted with error: {e}')
        exit(1)
        
    guiThread.join()
    logger.info('gui thread finished, exiting...')


if __name__ == '__main__':
    logger.debug(f'{VERSION=} {DEBUG=}')
    _start()
