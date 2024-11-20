import gzip
import os
from properties import *
from logger import logger


def compress(targetPath:str, sch:dict) -> str:
    logger.info('gz compressing...')
    
    zipPath = f'{targetPath}.gz'
    compressLevel = sch.get('compressLevel', 5)
    password = sch.get('password')
    if password:
        logger.warning(f'Internal GZ archiver does not support password; archive will not encrypted')

    tfile = open(targetPath, 'rb')
    zfile = open(zipPath, 'wb')
    data = gzip.compress(tfile.read(), compressLevel)
    zfile.write(data)

    tfile.close()
    zfile.close()
    logger.info('compress finished with success!')
    return os.path.basename(zipPath)


def decompress(archPath:str, sch:dict, schemaName:str) -> str:
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
