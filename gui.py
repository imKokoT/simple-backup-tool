import threading
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
    # guiThread = Thread(target=)
    guiImport = """from plugins.gui.main import start_gui"""

    try:
        exec(guiImport)
    # except ModuleNotFoundError as e:
    #     logger.fatal(f'failed to import gui plugin from plugins folder! error: {e}')
    #     exit(1)
    except Exception as e:
        logger.fatal(f'importing of gui plugin interrupted with error: {e}')
        exit(1)
        

if __name__ == '__main__':
    logger.debug(f'{VERSION=} {DEBUG=}')
    _start()
