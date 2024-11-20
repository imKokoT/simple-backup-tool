import io
import json
import os
import tarfile
import time
from properties import *
from logger import logger


def configurePack(archive:tarfile.TarFile, backupSchema:dict, packedTargets:list):
    logger.info('configuring pack...')

    if not backupSchema.get('destination'):
        logger.fatal(f'failed to get "destination" param from schema')
        exit(1)

    data = {
        'creation-time': time.time(),
        'destination': backupSchema['destination'],
        'root': backupSchema.get('destination'),
        'files': [p for p in packedTargets if os.path.isfile(p)],
        'folders': [p for p in packedTargets if os.path.isdir(p)]
    }

    meta = tarfile.TarInfo('config')
    if DEBUG:
        jsonData = json.dumps(data, indent=2)
    else:
        jsonData = json.dumps(data, separators=(',',':'))
    
    jsonData = io.BytesIO(jsonData.encode())
    meta.size = len(jsonData.getvalue())

    archive.addfile(meta, fileobj=jsonData)


def loadPackConfig(archive:tarfile.TarFile) -> dict:
    '''returns pack's config'''
    logger.info('loading pack\'s config...')

    if 'config' not in archive.getnames():
        logger.fatal('bad pack: config not found')
        exit(1)

    configFile = archive.extractfile('config')
    data = json.loads(configFile.read())
    configFile.close()
    return data
