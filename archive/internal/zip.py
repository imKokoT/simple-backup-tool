import zipfile
import os
from config import *
from tools import updateProgressBar


def compress(targetPath:str, sch:dict) -> str:
    programLogger.info('zip compressing...')
    zipPath = f'{targetPath}.zip'

    zfile = zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_DEFLATED)
    tfile = open(targetPath, 'rb')
    tsize = os.path.getsize(targetPath) 

    zip_info = zipfile.ZipInfo(os.path.basename(targetPath))
    processedSize = 0
    with zfile.open(zip_info, 'w') as z:
        while True:
            data = tfile.read(COMPRESS_CHUNK_SIZE)
            if not data:
                break
            
            z.write(data)
            
            processedSize += len(data)
            updateProgressBar(processedSize / tsize)

    zfile.close()
    tfile.close()
    programLogger.info('compress finished with success!')
    return zipPath


def decompress(archPath:str, sch:dict):
    pass