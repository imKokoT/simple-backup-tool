import threading
import importlib
from threading import Event, Thread
from logger import logger
from properties import *
from runtime_data import rtd


def _eventHandler():
    event = Event()

    while True:
        # events...
        event.wait(EVENT_UPDATE_DELAY)


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
