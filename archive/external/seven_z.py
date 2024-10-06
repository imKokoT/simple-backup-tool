import os
import subprocess
from config import *

def compress(targetPath:str, sch:dict) -> str:
    programLogger.info('7z compressing...')
    
    zipPath = f'{targetPath}.7z'
    compressLevel = sch.get('compressLevel', 5)
    password = sch.get('password')
    
    command = ['7z', 'a', '-t7z', f'-mx={compressLevel}', zipPath, targetPath]
    if password:
        command.append(f'-p{password}')
        command.append('-mhe=on')

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        programLogger.info("compress finished with success!")
    else:
        programLogger.fatal(f"external process error: {result.stderr}")
        exit(1)

    return os.path.basename(zipPath)


def decompress(archPath:str, sch:dict, schemaName:str) -> str:
    programLogger.info('7z decompressing...')

    exportPath = os.path.join(os.path.dirname(archPath), f'{schemaName}.tar')
    password = sch.get('password')
    command = ['7z', 'x', archPath, f'-o{os.path.dirname(exportPath)}']
    if password:
        command.append(f'-p{password}')

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        programLogger.info("decompress finished with success!")
    else:
        programLogger.fatal(f"external process error: {result.stderr}")
        exit(1)

    return os.path.basename(exportPath)
