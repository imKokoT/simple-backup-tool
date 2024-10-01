import bz2
import os
from config import *

def compress(targetPath:str, sch:dict) -> str:
    programLogger.info('bz2 compressing...')
    
    zipPath = f'{targetPath}.bz2'
    compressLevel = sch.get('compressLevel', 5)
    password = sch.get('password')
    if password:
        programLogger.warning(f'Internal BZ2 archiver does not support password; archive will not encrypted')

    tfile = open(targetPath, 'rb')
    zfile = open(zipPath, 'wb')
    data = bz2.compress(tfile.read())
    zfile.write(data)

    tfile.close()
    zfile.close()
    programLogger.info('compress finished with success!')
    return os.path.basename(zipPath)


def decompress(archPath:str, sch:dict, schemaName:str) -> str:
    programLogger.info('bz2 decompressing...')

    exportPath = os.path.join(os.path.dirname(archPath), f'{schemaName}.tar')
    efile = open(exportPath, 'wb')
    zfile = open(archPath, 'rb')
    
    data = bz2.decompress(zfile.read())
    efile.write(data)

    zfile.close()
    efile.close()
    programLogger.info('decompress finished with success!')
    return os.path.basename(exportPath)