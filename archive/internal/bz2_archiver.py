import bz2
import os
from miscellaneous.miscellaneous import humanSize
from properties import *
from logger import logger
from runtime_data import rtd


def compress(targetPath:str) -> str:
    logger.info('bz2 compressing...')

    schema:dict = rtd['schema']    
    zipPath = f'{targetPath}.bz2'
    compressLevel = schema.get('compressLevel', 5)
    password = schema.get('password')
    if password:
        logger.warning(f'Internal BZ2 archiver does not support password; archive will not encrypted')

    tfile = open(targetPath, 'rb')
    zfile = open(zipPath, 'wb')
    data = bz2.compress(tfile.read(), compressLevel)
    zfile.write(data)

    tfile.close()
    zfile.close()
    zsize = os.path.getsize(zipPath)
    logger.info(f'compress finished with success! compressed size: {humanSize(zsize)}')
    return os.path.basename(zipPath)


def decompress(archPath:str, schemaName:str) -> str:
    logger.info('bz2 decompressing...')

    exportPath = os.path.join(os.path.dirname(archPath), f'{schemaName}.tar')
    efile = open(exportPath, 'wb')
    zfile = open(archPath, 'rb')
    
    data = bz2.decompress(zfile.read())
    efile.write(data)

    zfile.close()
    efile.close()
    logger.info('decompress finished with success!')
    return os.path.basename(exportPath)
