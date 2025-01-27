from logger import logger
import encryption


def encrypt(schema:dict, archName:str) -> str:
    if not schema.get('encryption'):
        logger.debug('encryption skipped')
        return archName
    try:
        import cryptography as _
    except ModuleNotFoundError:
        logger.warning(f'encryption not available, use "pip install cryptography"; encryption skipped.')
        return archName
    
    match schema['encryption']:
        case 'aes': return encryption.aes.encrypt(schema, archName)
        case 'chacha20': return encryption.chacha20poly1305.encrypt(schema, archName)
        case _:
            logger.fatal(f'unsupported algorism "{schema["encryption"]}"')
            exit(1)

def decrypt(schema:dict):
    try:
        import cryptography as _
    except ModuleNotFoundError:
        logger.fatal(f'decryption not available, use "pip install cryptography"')
        exit(1)
    
    try:
        match schema['encryption']:
            case 'aes': return encryption.aes.decrypt(schema)
            case 'chacha20': return encryption.chacha20poly1305.decrypt(schema)
            case _:
                logger.fatal(f'unsupported algorism "{schema["encryption"]}"')
                exit(1)
    except ValueError as e:
        logger.debug(f'decryption process exited with error: {e}')
        logger.error('failed to decrypt archive; possibly wrong password')
        exit(1)
