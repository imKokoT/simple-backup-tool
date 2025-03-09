import zipfile
import os
from properties import *
from miscellaneous.miscellaneous import humanSize, updateProgressBar
from logger import logger
from runtime_data import rtd


def compress(targetPath:str) -> str:
    logger.info('zip compressing...')
    
    schema:dict = rtd['schema']
    zipPath = f'{targetPath}.zip'
    compressLevel = schema.get('compressLevel', 5)
    password = schema.get('password')

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
    zsize = os.path.getsize(zipPath)
    logger.info(f'compress finished with success! compressed size: {humanSize(zsize)}')
    return os.path.basename(zipPath)


def decompress(archPath:str, schemaName:str):
    logger.info('zip decompressing...')

    schema:dict = rtd['schema']
    exportPath = os.path.join(os.path.dirname(archPath), f'{schemaName}.tar')
    
    zfile = zipfile.ZipFile(archPath, 'r')
    esize = zfile.getinfo(f'{schemaName}.tar').file_size

    zfile.extract(f'{schemaName}.tar', os.path.dirname(exportPath), 
                  bytes(schema.get('password'), 'utf-8') if schema.get('password') else None)

    zfile.close()
    logger.info('decompress finished with success!')
    return os.path.basename(exportPath)
