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
    logger.info(f'encrypting...')
    with open(archivePath, 'rb') as ifile, open(ArchiveTMPPath, 'wb') as ofile:
        ofile.write(iv)

        chunkI = 0
        fSize = os.path.getsize(archivePath)
        while chunk := ifile.read(CHUNK_SIZE):
            if len(chunk) < CHUNK_SIZE:
                chunk = padder.update(chunk) + padder.finalize()

            encrypted_chunk = encryptor.update(chunk)
            ofile.write(encrypted_chunk)
            chunkI += 1
            updateProgressBar(chunkI/(fSize/CHUNK_SIZE))
        ofile.write(encryptor.finalize())

    logger.info(f'deleting duplicate')
    os.remove(archivePath)
    os.rename(ArchiveTMPPath, archivePath)

    logger.info(f"encryption completed with success!")
    return archivePath


def decrypt(schema:dict):
    logger.info('initialize decryption process with AES-256')
    tmp = getTMP()
    schemaName = schema['__name__']
    downloaded = f'{tmp}/{schemaName}.downloaded'
    downloadedTMP = f'{downloaded}.tmp'

    if not schema.get('password'):
        logger.fatal(f'failed to decrypt: decryption process require "password" parameter!')
        exit(1)
    # TODO: implement salt
    key = keygen(schema['password'], b'')
    
    logger.info('decrypting...')
    with open(downloaded, 'rb') as ifile, open(downloadedTMP, 'wb') as ofile:
        iv = ifile.read(IV_SIZE)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

        chunkI = 0
        fSize = os.path.getsize(downloaded)
        while chunk := ifile.read(CHUNK_SIZE):
            decrypted_chunk = decryptor.update(chunk)
            if len(decrypted_chunk) < CHUNK_SIZE:
                decrypted_chunk = unpadder.update(decrypted_chunk) + unpadder.finalize()

            ofile.write(decrypted_chunk)
            chunkI += 1
            updateProgressBar(chunkI/(fSize/CHUNK_SIZE))
        ofile.write(decryptor.finalize())

    logger.info(f'deleting duplicate')
    os.remove(downloaded)
    os.rename(downloadedTMP, downloaded)

    logger.info(f"decryption completed with success!")
