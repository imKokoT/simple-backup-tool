from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from .keygen import bytesgen, keygen
from logger import logger
from miscellaneous import getTMP, updateProgressBar
import os

IV_SIZE = 16
CHUNK_SIZE = 1024 * 1024


def encrypt(schema:dict, archiveName:str) -> str:
    logger.info('initialize encryption process with AES-256')
    iv = bytesgen(IV_SIZE)

    if not schema.get('password'):
        logger.fatal(f'failed to encrypt: encryption process require "password" parameter!')
        exit(1)

    # TODO: implement salt
    key = keygen(schema['password'], b'')
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()    
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    tmp = getTMP()

    archivePath = f'{tmp}/{archiveName}'
    ArchiveTMPPath = f'{archivePath}.tmp'
    with open(archivePath, 'rb') as ifile, open(ArchiveTMPPath, 'wb') as ofile:
        ofile.write(iv)

        while chunk := ifile.read(CHUNK_SIZE):
            if len(chunk) < CHUNK_SIZE:
                chunk = padder.update(chunk) + padder.finalize()

            encrypted_chunk = encryptor.update(chunk)
            ofile.write(encrypted_chunk)
            # updateProgressBar()
        ofile.write(encryptor.finalize())

    logger.info(f'deleting duplicate')
    os.remove(archivePath)
    os.rename(ArchiveTMPPath, archivePath)

    logger.info(f"encryption completed with success!")
    return archivePath
