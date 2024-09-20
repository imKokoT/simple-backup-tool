import os
import tarfile
from config import *
import schema
import time
import json
import io


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
    
    if not sch.get('folders'):
        programLogger.fatal(f'failed to get "folders" key from schema "{schemaName}"')
        exit(1)

    packedCount = 0
    packedFolders = []
    result = {
        'files':0,
        'ignored': 0,
        'size': 0,
        'scannedSize': 0
    }
    res:dict
    for dir in sch['folders']:
        res = pack(dir, archive)

        if res:
            packedFolders.append(dir)
            for k in res.keys():
                result[k] += res[k]
            packedCount += 1

    configurePack(archive, sch, packedFolders)

    programLogger.info(f'packing process finished successfully;\n'
                       f' - packs created: {packedCount}/{len(sch["folders"])}\n'
                       f' - archived and ignored total files: {result['files']}/{result['ignored']}\n'
                       f' - archived total size: {result["size"]}/{result["scannedSize"]}'
                       )
    archive.close()


def pack(targetFolder:str, archive:tarfile.TarFile):
    if not os.path.exists(targetFolder):
        programLogger.error(f'packing failed: target folder "{targetFolder}" not exists')
        return

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
    
    for f in files:
        dpath = os.path.join(os.path.basename(targetFolder),f)
        archive.add(os.path.join(targetFolder, f), arcname=dpath)
    
    programLogger.info(f'success')
    return {
        'files':len(files),
        'ignored': ignored,
        'size': packSize,
        'scannedSize': scannedSize
        }


def configurePack(archive:tarfile.TarFile, backupSchema:dict, packedFolders:list):
    programLogger.info('configuring pack...')

    if not backupSchema.get('destination'):
        programLogger.fatal(f'failed to get "destination" param from schema')
        exit(1)

    data = {
        'creation-time': time.time(),
        'destination': backupSchema['destination'],
        'packs': { os.path.basename(p): p for p in packedFolders }
    }

    meta = tarfile.TarInfo('config')
    if DEBUG:
        jsonData = json.dumps(data, indent=2)
    else:
        jsonData = json.dumps(data, separators=(',',':'))
    
    jsonData = io.BytesIO(jsonData.encode())
    meta.size = len(jsonData.getvalue())

    archive.addfile(meta, fileobj=jsonData)


def unpack(targetFolder:str, archive:tarfile.TarFile):
    if os.path.exists(targetFolder) and not ALLOW_LOCAL_REPLACE:
        targetFolder = os.path.join(os.path.dirname(targetFolder), os.path.basename(targetFolder) + '-restored')

    print(targetFolder)


def unpackAll(schemaName:str, schema:dict):
    if ALLOW_LOCAL_REPLACE and ASK_BEFORE_REPLACE:
        print(f'{LYC}Are you sure to rewrite next folders:')
        for f in schema['folders']:
            print(f'{LYC} - {f}')
        yn = input('[y/N] ')
        if yn.strip().lower() != 'y':
            print('restored data placed in tmp folder\nunpack process interrupted...')
            exit(0)
    
