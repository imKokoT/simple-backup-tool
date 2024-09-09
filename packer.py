import os
import tarfile
from config import *

def pack(targetFolder:str, archive:str):
    programLogger.info(f'packing "{targetFolder}"; reading content...')
    files = []
    ignored = 0
    scannedSize = 0
    packSize = 0
    for dpath, _, fnames in os.walk(targetFolder):
        for fname in fnames:
            relative_path = os.path.relpath(os.path.join(dpath, fname), targetFolder)
            files.append(relative_path)

            packSize += os.path.getsize(os.path.join(targetFolder, relative_path))
    programLogger.info(f'reading success; total files: {len(files)} [{packSize}B/{scannedSize}B]; ignored total: {ignored}')


