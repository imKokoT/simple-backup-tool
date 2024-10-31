import zipfile
import os
from config import *
from miscellaneous import updateProgressBar


def compress(targetPath:str, sch:dict) -> str:
    logger.info('zip compressing...')
    
    zipPath = f'{targetPath}.zip'
    compressLevel = sch.get('compressLevel', 5)
    password = sch.get('password')

    zfile = zipfile.ZipFile(
        zipPath, 'w',
        compression=zipfile.ZIP_DEFLATED, 
        compresslevel=compressLevel
        )
    if password:
        logger.warning(f'Internal zip archiver does not support password; archive will not encrypted')
    tfile = open(targetPath, 'rb')
    tsize = os.path.getsize(targetPath) 

    zfile.writestr(os.path.basename(targetPath), tfile.read())

    tfile.close()
    zfile.close()
    logger.info('compress finished with success!')
    return os.path.basename(zipPath)


def decompress(archPath:str, sch:dict, schemaName:str):
    logger.info('zip decompressing...')

    exportPath = os.path.join(os.path.dirname(archPath), f'{schemaName}.tar')
    
    zfile = zipfile.ZipFile(archPath, 'r')
    esize = zfile.getinfo(f'{schemaName}.tar').file_size

    zfile.extract(f'{schemaName}.tar', os.path.dirname(exportPath), 
                  bytes(sch.get('password'), 'utf-8') if sch.get('password') else None)

    zfile.close()
    logger.info('decompress finished with success!')
    return os.path.basename(exportPath)
