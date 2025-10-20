#!/usr/bin/env python3
import logging
import importlib
import socket
import json
from threading import Event, Thread
from logger import logger, BASE_LOGGING_FORMAT
from properties import *
from runtime_data import rtd
from miscellaneous.events import EventLogHandler
from miscellaneous.miscellaneous import catchCritical

PORT = 22320

def _dump(data:dict) -> bytes:
    return json.dumps(data, separators=(',',':')).encode()

def _decode(data:bytes) -> dict:
    return json.loads(data.decode())


def _eventListener():
    event = Event()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', PORT))
    server.listen()
    logger.info(f'server is running at port {PORT}')

    conn, addr = server.accept()
    with conn:
        logger.info(f'connected {addr}')
        
        # handshake
        conn.sendall(_dump({
            'version': VERSION
        }))
        msg = conn.recv(1024).decode()
        if msg != 'ACCEPTED':
            logger.error(f'handshake error: client refused connection with error "{msg}"')
            return

        while True:
            # events...
            event.wait(EVENT_UPDATE_DELAY)


@catchCritical
def _start():
    logger.info('stating SBT server...')
    rtd['gui'] = True
    eventHandlerThread = Thread(target=_eventListener, daemon=True)
    
    eventHandlerThread.start()
    eventHandlerThread.join()
    
    # guiThread:Thread = None

    # logger.info('importing gui plugin')
    # try:
    #     guiModule = importlib.import_module('plugins.gui.main')
    #     start_gui = getattr(guiModule, 'start_gui', None)
    #     guiThread = Thread(target=start_gui, daemon=True)
    # except ModuleNotFoundError as e:
    #     logger.fatal(f'failed to import gui plugin from plugins folder! error: {e}')
    #     exit(1)
    # except Exception as e:
    #     logger.fatal(f'importing of gui plugin interrupted with error: {e}')
    #     exit(1)
    
    # eventHandlerThread.start()
    
    # # add new logger handler to push logs as events
    # handler = EventLogHandler()
    # handler.setFormatter(logging.Formatter(BASE_LOGGING_FORMAT))
    # logger.addHandler(handler)

    # logger.info('starting gui thread')
    # try:
    #     guiThread.start()
    # except Exception as e:
    #     logger.fatal(f'starting gui plugin interrupted with error: {e}')
    #     exit(1)
        
    # guiThread.join()
    # logger.info('gui thread finished, exiting...')


if __name__ == '__main__':
    logger.debug(f'{VERSION=} {DEBUG=}')
    _start()
