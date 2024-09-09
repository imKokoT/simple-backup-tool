import os
import tarfile
from config import *
import schema


def packAll(schemaName:str):
    programLogger.info('packing process started')
    sch = schema.getBackupSchema(schemaName)
    if not sch: 
        programLogger.fatal(f'packing process failed: no schema "{schemaName}"')
        exit(1)
    
    if DEBUG:
        if not os.path.exists('./debug'): os.mkdir('./debug')
        if not os.path.exists('./debug/tmp'): os.mkdir('./debug/tmp')
        tmp = './debug/tmp'

    archive = tarfile.open(os.path.join(tmp, f'{schemaName}.tar'), 'w')
    
    if not sch.get('folders', None):
        programLogger.fatal(f'failed to get "folders" key from schema "{schemaName}"')
        exit(1)

    packedCount = 0
    for dir in sch['folders']:
        res = pack(dir, archive)

    programLogger.info(f'packing process finished successfully; packs created: {packedCount}/{len(sch["folders"])}')
    archive.close()



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
            scannedSize += os.path.getsize(os.path.join(targetFolder, relative_path))

    programLogger.info(f'reading success; total files: {len(files)} [{packSize}B/{scannedSize}B]; ignored total: {ignored}')


    

    programLogger.info(f'adding to archive...')
    with tarfile.open(os.path.join(tmp, archive), 'x') as t:
        for f in files:
            t.add(os.path.join(targetFolder, f), arcname=f)
    programLogger.info(f'success')
