import gzip
import os
from miscellaneous.miscellaneous import humanSize
from properties import *
from logger import logger
from runtime_data import rtd


def compress(targetPath:str) -> str:
    logger.info('gz compressing...')
    
    schema:dict = rtd['schema']
    zipPath = f'{targetPath}.gz'
    compressLevel = schema.get('compressLevel', 5)
    password = schema.get('password')
    if password:
        logger.warning(f'Internal GZ archiver does not support password; archive will not encrypted')

    tfile = open(targetPath, 'rb')
    zfile = open(zipPath, 'wb')
    data = gzip.compress(tfile.read(), compressLevel)
    zfile.write(data)

    tfile.close()
    zfile.close()
    zsize = os.path.getsize(zipPath)
    logger.info(f'compress finished with success! compressed size: {humanSize(zsize)}')
    return os.path.basename(zipPath)


def decompress(archPath:str, schemaName:str) -> str:
    logger.info('gz decompressing...')

    exportPath = os.path.join(os.path.dirname(archPath), f'{schemaName}.tar')
    efile = open(exportPath, 'wb')
    zfile = open(archPath, 'rb')
    
    data = gzip.decompress(zfile.read())
    efile.write(data)

    zfile.close()
    efile.close()
    logger.info('decompress finished with success!')
    return os.path.basename(exportPath)
