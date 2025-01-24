from encryption.keygen import bytesgen, keygen
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from logger import logger
from miscellaneous import getTMP, updateProgressBar
import os

CHUNK_SIZE = 1024 * 1024
NONCE_SIZE = 16

def encrypt(schema:dict, archiveName:str) -> str:
    logger.info('initialize encryption process with ChaCha20')
    nonce = bytesgen(NONCE_SIZE)

    if not schema.get('password'):
        logger.fatal(f'failed to decrypt: decryption process require "password" parameter!')
        exit(1)
    # TODO: implement salt
    key = keygen(schema['password'], b'')
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
    encryptor = cipher.encryptor()
    tmp = getTMP()

    archivePath = f'{tmp}/{archiveName}'
    ArchiveTMPPath = f'{archivePath}.tmp'
    logger.info(f'encrypting...')
    with open(archivePath, 'rb') as ifile, open(ArchiveTMPPath, 'wb') as ofile:
        ofile.write(nonce)

        chunkI = 0
        fSize = os.path.getsize(archivePath)
        while chunk := ifile.read(CHUNK_SIZE):
            encrypted_chunk = encryptor.update(chunk)
            ofile.write(encrypted_chunk)
            chunkI += 1
            updateProgressBar(chunkI/(fSize/CHUNK_SIZE))
        
        logger.info('finalizing...')
        ofile.write(encryptor.finalize())

    logger.info(f'deleting duplicate')
    os.remove(archivePath)
    os.rename(ArchiveTMPPath, archivePath)

    logger.info(f"encryption completed with success!")
    return archivePath


def decrypt(schema:dict):
    logger.info('initialize decryption process with ChaCha20')
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
        nonce = ifile.read(NONCE_SIZE)

        key = keygen(schema['password'], b'')
        cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
        decryptor = cipher.decryptor()
        
        chunkI = 0
        fSize = os.path.getsize(downloaded)
        while chunk := ifile.read(CHUNK_SIZE):
            decrypted_chunk = decryptor.update(chunk)
            ofile.write(decrypted_chunk)
            chunkI += 1
            updateProgressBar(chunkI/(fSize/CHUNK_SIZE))
        
        logger.info('finalizing...')
        ofile.write(decryptor.finalize())

    logger.info(f'deleting duplicate')
    os.remove(downloaded)
    os.rename(downloadedTMP, downloaded)

    logger.info(f"decryption completed with success!")
