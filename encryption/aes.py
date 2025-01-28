# AES-256
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
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

    # TODO: implement salt
    key = keygen(schema['_enc_keyword'], b'')
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
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

            encryptedChunk = encryptor.update(chunk)
            ofile.write(encryptedChunk)
            chunkI += 1
            updateProgressBar(chunkI/(fSize/CHUNK_SIZE))
        
        logger.info('finalizing...')
        ofile.write(encryptor.finalize())

    logger.info(f'deleting duplicate')
    os.remove(archivePath)
    os.rename(ArchiveTMPPath, archivePath)

    logger.info(f"encryption completed with success!")
    return archiveName


def decrypt(schema:dict):
    logger.info('initialize decryption process with AES-256')
    tmp = getTMP()
    schemaName = schema['__name__']
    downloaded = f'{tmp}/{schemaName}.downloaded'
    downloadedTMP = f'{downloaded}.tmp'

    # TODO: implement salt
    key = keygen(schema['_enc_keyword'], b'')
    
    logger.info('decrypting...')
    with open(downloaded, 'rb') as ifile, open(downloadedTMP, 'wb') as ofile:
        iv = ifile.read(IV_SIZE)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

        chunkI = 0
        fSize = os.path.getsize(downloaded)
        while chunk := ifile.read(CHUNK_SIZE):
            decryptedChunk = decryptor.update(chunk)
            if len(decryptedChunk) < CHUNK_SIZE:
                decryptedChunk = unpadder.update(decryptedChunk) + unpadder.finalize()

            ofile.write(decryptedChunk)
            chunkI += 1
            updateProgressBar(chunkI/(fSize/CHUNK_SIZE))
            
        logger.info('finalizing...')
        ofile.write(decryptor.finalize())

    logger.info(f'deleting duplicate')
    os.remove(downloaded)
    os.rename(downloadedTMP, downloaded)

    logger.info(f"decryption completed with success!")
