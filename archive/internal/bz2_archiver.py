import bz2
import os
from config import *

def compress(targetPath:str, sch:dict) -> str:
    logger.info('bz2 compressing...')
    
    zipPath = f'{targetPath}.bz2'
    compressLevel = sch.get('compressLevel', 5)
    password = sch.get('password')
    if password:
        logger.warning(f'Internal BZ2 archiver does not support password; archive will not encrypted')

    tfile = open(targetPath, 'rb')
    zfile = open(zipPath, 'wb')
    data = bz2.compress(tfile.read(), compressLevel)
    zfile.write(data)

    tfile.close()
    zfile.close()
    logger.info('compress finished with success!')
    return os.path.basename(zipPath)


def decompress(archPath:str, sch:dict, schemaName:str) -> str:
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
