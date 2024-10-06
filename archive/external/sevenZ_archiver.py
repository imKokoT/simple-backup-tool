import os
import subprocess
from config import *

def compress(targetPath:str, sch:dict) -> str:
    
    compressLevel = sch.get('compressLevel', 5)
    password = sch.get('password')
    match sch.get('compressFormat', '7z'):
        case '7z': compressFormat = '7z'
        case 'zip': compressFormat = 'zip'
        case 'bz2': compressFormat = 'bzip2'
        case 'gz': compressFormat = 'gzip'
        case 'xz': compressFormat = 'xz'
        case _:
            programLogger.fatal(f'compression format {sch.get('compressFormat', '7z')} not supports in 7z or in this tool')
            exit(1)

    zipPath = f'{targetPath}.{sch.get('compressFormat', '7z')}'
    programLogger.info(f'{sch.get('compressFormat', '7z')} with 7z subprocess compressing...')
    
    command = ['7z', 'a', '-y', f'-t{compressFormat}', f'-mx={compressLevel}', zipPath, targetPath]
    if password:
        if sch.get('compressFormat', '7z') == '7z':
            command.append(f'-p{password}')
            command.append('-mhe=on')
        elif sch.get('compressFormat', '7z') == 'zip':
            command.append(f'-p{password}')
            command.append('-mem=AES256')
        else:
            programLogger.warning(f'7z not supports password for "{sch.get('compressFormat', '7z')}". archive will not encrypted')

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        programLogger.info("compress finished with success!")
    else:
        programLogger.fatal(f"external process error: {result.stderr}")
        exit(1)

    return os.path.basename(zipPath)


def decompress(archPath:str, sch:dict, schemaName:str) -> str:
    programLogger.info('7z subprocess decompressing...')

    exportPath = os.path.join(os.path.dirname(archPath), f'{schemaName}.tar')
    password = sch.get('password')
    command = ['7z', 'x', '-y', archPath, f'-o{os.path.dirname(exportPath)}']
    if password:
        command.append(f'-p{password}')

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        programLogger.info("decompress finished with success!")
    else:
        programLogger.fatal(f"external process error: {result.stderr}")
        exit(1)

    return os.path.basename(exportPath)
