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
        case 'chacha20': return encryption.chacha20.encrypt(schema, archName)
        case _:
            logger.fatal(f'unsupported encryption algorism "{schema["encryption"]}"')
            exit(1)

def decrypt(schema:dict): ...
