import os
import tarfile
from config import *
import schema
import time
import json
import io
from miscellaneous import getTMP


def packAll(schemaName:str):
    programLogger.info('packing process started')
    sch = schema.getBackupSchema(schemaName)
    if not sch: 
        programLogger.fatal(f'packing process failed: no schema "{schemaName}"')
        exit(1)
    
    tmp = getTMP()

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
    for item in sch['folders']:
        if os.path.isfile(item):
            res = packFile(item, archive)
        else:
            res = packFolder(item, archive)

        if res:
            packedFolders.append(item)
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


def packFolder(targetFolder:str, archive:tarfile.TarFile):
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


def packFile(targetFile:str, archive:tarfile.TarFile):
    if not os.path.exists(targetFile):
        programLogger.error(f'packing failed: target file "{targetFile}" not exists')
        return
    programLogger.info(f'packing target file "{targetFile}"')

    isIgnored = False
    size = os.path.getsize(targetFile)

    archive.add(targetFile, f'files/{os.path.basename(targetFile)}')

    return {
        'files': not isIgnored,
        'ignored': isIgnored,
        'size': size if not isIgnored else 0,
        'scannedSize': size
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


def loadPackConfig(archive:tarfile.TarFile) -> dict:
    '''returns pack's config'''
    programLogger.info('loading pack\'s config...')

    if 'config' not in archive.getnames():
        programLogger.fatal('bad pack: config not found')
        exit(1)

    configFile = archive.extractfile('config')
    data = json.loads(configFile.read())
    configFile.close()
    return data


def unpack(name:str, targetFolder:str, archive:tarfile.TarFile):
    programLogger.info(f'unpacking "{name}"...')
    
    if not os.path.exists(os.path.dirname(targetFolder)):
        programLogger.error(f'failed to unpack because "{os.path.dirname(targetFolder)}" not exists')
        return
    
    if os.path.exists(targetFolder) and not ALLOW_LOCAL_REPLACE:
        targetFolder = os.path.join(os.path.dirname(targetFolder), os.path.basename(targetFolder) + '-restored')
        if os.path.exists(targetFolder):
            os.rmdir(targetFolder)
        os.mkdir(targetFolder)
    elif not os.path.exists(targetFolder):
        os.mkdir(targetFolder)

    rewrittenCount = 0
    restoredCount = 0

    for member in archive.getmembers():
        if not (member.name.startswith(name) and member.isfile()):
            continue

        relpath = os.path.relpath(member.name, name)
        targetFilePath = os.path.join(targetFolder, relpath)

        if os.path.exists(targetFilePath):
            rewrittenCount += 1
        else:
            restoredCount += 1

        os.makedirs(os.path.dirname(targetFilePath), exist_ok=True)

        with archive.extractfile(member) as file_obj:
            with open(targetFilePath, 'wb') as out_file:
                out_file.write(file_obj.read())

    programLogger.info(f'success! unpacked to "{targetFolder}"\n'
                       f' - rewritten: {rewrittenCount}\n'
                       f' - restored: {restoredCount}')
    return {
        'rewritten': rewrittenCount,
        'restored': restoredCount
    }


def unpackAll(schemaName:str, schema:dict):
    programLogger.info('unpacking process started')
   
    tmp = getTMP()
    archive = tarfile.open(os.path.join(tmp, f'{schemaName}.tar'), 'r')

    packConfig = loadPackConfig(archive)
    
    if ALLOW_LOCAL_REPLACE and ASK_BEFORE_REPLACE:
        print(f'{LYC}Are you sure to rewrite next folders:')
        for f in packConfig['packs'].values():
            print(f'{LYC} - {f}')
        yn = input('[y/N] ')
        if yn.strip().lower() != 'y':
            print('restored data placed in tmp folder\nunpack process interrupted...')
            exit(0) 

    result = {
        'rewritten': 0,
        'restored': 0
    }
    res:dict
    for name, path in packConfig['packs'].items():
        res = unpack(name, path, archive)

        result['rewritten'] += res['rewritten']
        result['restored'] += res['restored']

    programLogger.info(f'unpacking finished with success!\n'
                       f' - rewritten total: {result['rewritten']}\n'
                       f' - restored total: {result["restored"]}')
    archive.close()