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


def decompress(archPath:str, sch:dict, schemaName:str):
    programLogger.info('zip decompressing...')

    exportPath = os.path.join(os.path.dirname(archPath), f'{schemaName}.tar')
    
    zfile = zipfile.ZipFile(archPath, 'r')
    efile = open(exportPath, 'wb')
    esize = zfile.getinfo(f'{schemaName}.tar').file_size

    processedSize = 0
    with zfile.open(f'{schemaName}.tar', 'r') as t:
        while True:
            data = t.read(COMPRESS_CHUNK_SIZE)
            if not data:
                break
            
            processedSize = efile.write(data)
            
            updateProgressBar(processedSize / esize)

    zfile.close()
    efile.close()
    programLogger.info('compress finished with success!')
