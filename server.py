#!/usr/bin/env python3
import logging
import importlib
import socket
import json
from threading import Event, Thread
from logger import logger, BASE_LOGGING_FORMAT
from properties import *
from runtime_data import rtd
from backup import createBackupOf
from miscellaneous.events import EventLogHandler, pushEvent, getEvent, tryPopEvent
from miscellaneous.miscellaneous import catchCritical

PORT = 22320
EVENT_BUFSIZE = 1024*4


def _dump(data:dict) -> bytes:
    return json.dumps(data, separators=(',',':')).encode()

def _decode(data:bytes) -> dict:
    return json.loads(data.decode())


def _eventHandler():
    te = Event()

    try:
        while True:
            if msg := tryPopEvent('log-pushed'):
                conn:socket.socket = rtd['connection']
                if not conn: continue
                conn.sendall(
                    json.dumps(
                        {
                            'event': 'send-logs',
                            'msg': msg
                        }
                    ).encode()
                )

            if msg := getEvent('backup'):
                Thread(target=createBackupOf, args=[msg['schemaName']]).start()

            if msg := getEvent('restore'):
                logger.info(f'restore: {msg}')
            
            if getEvent('QUIT'):
                logger.info('quit server...')
                quit(0)

            te.wait(EVENT_UPDATE_DELAY)
    except Exception as e:
        msg = f'while was handling events, the exception raised: {e}'
        logger.exception(msg)
        quit(1)


def _eventListener():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', PORT))
    server.listen()
    rtd['server'] = server
    logger.info(f'server is running at port {PORT}')

    conn, addr = server.accept()
    with conn:
        logger.info(f'connected {addr}')
        
        # handshake
        conn.sendall(_dump({
            'version': VERSION
        }))
        msg = conn.recv(1024).decode()
        if msg != 'ACCEPTED' or not msg:
            logger.error(f'handshake error: client refused connection with error "{msg}"')
            return
        rtd['connection'] = conn        

        # listen events
        while True:
            r = conn.recv(EVENT_BUFSIZE)
            if not r:
                logger.error('client dropped connection')
                pushEvent('QUIT', internal=True)
                return
            
            try:
                eventData = _decode(r)
                pushEvent(eventData['event'], eventData['msg'], internal=True)
            except Exception as e:
                logger.exception(f'bad event!\nresponse body: {r}')


@catchCritical
def _start():
    logger.info('stating SBT server...')
    rtd['gui'] = True
    rtd['events'] = {}
    eventListenerThread = Thread(target=_eventListener, daemon=True)
    eventHandlerThread = Thread(target=_eventHandler, daemon=True)

    # # add new logger handler to push logs as events
    handler = EventLogHandler()
    handler.setFormatter(logging.Formatter(BASE_LOGGING_FORMAT))
    logger.addHandler(handler)

    eventHandlerThread.start()
    eventListenerThread.start()
    eventListenerThread.join()
    
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
