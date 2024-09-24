import zipfile
import os
from config import *
from tools import updateProgressBar


def compress(targetPath:str, sch:dict) -> str:
    programLogger.info('zip compressing...')
    
    zipPath = f'{targetPath}.zip'
    compressLevel = sch.get('compressLevel', 5)
    password = sch.get('password')

    zfile = zipfile.ZipFile(
        zipPath, 'w',
        compression=zipfile.ZIP_DEFLATED, 
        compresslevel=compressLevel
        )
    if password:
        programLogger.warning(f'Internal zip archiver does not support password; archive will not encrypted')
    tfile = open(targetPath, 'rb')
    tsize = os.path.getsize(targetPath) 

    processedSize = 0
    while True:
        data = tfile.read(COMPRESS_CHUNK_SIZE)
        if not data:
            break
        
        zfile.writestr(os.path.basename(targetPath), data)
        processedSize += len(data)
        updateProgressBar(processedSize / tsize)

    zfile.close()
    tfile.close()
    programLogger.info('compress finished with success!')
    return zipPath


def decompress(archPath:str, sch:dict):
    pass