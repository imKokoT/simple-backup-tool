import os
import tarfile
from config import *
import schema
import time
import json
import io
import pathspec
from miscellaneous import getTMP


def loadIgnorePatterns(directory:str) -> pathspec.PathSpec|None:
    patterns = []

    for dpath, _, _ in os.walk(directory):
        ignoreFilers =(
            os.path.join(dpath, '.sbtignore'),
            os.path.join(dpath, '.gitignore')
        )
        for ignoreF in ignoreFilers:
            if not os.path.exists(ignoreF) or not Config().include_gitignore and os.path.basename(ignoreF) == '.gitignore': continue
            
            with open(ignoreF, 'r', encoding='utf-8') as f:
                for l in f.readlines():
                    l = f'{dpath[len(directory):]}/{l.strip()}'
                    l = f'!{l.replace('!', '')}' if '!' in l else l
                    l = l.replace('\\', '/').replace('//', '/')
                    patterns.append(l)
        if len(patterns) == 0:
            return

    return pathspec.PathSpec.from_lines('gitignore', patterns)


def shouldIgnore(path:str, specs:dict[str,pathspec.PathSpec], sorted_specs:list) -> bool:
    specPath = next(filter(lambda d: path.startswith(d), sorted_specs), None)
    spec = specs.get(specPath)
    return spec and spec.match_file(path[len(specPath):])


def packAll(schemaName:str):
    programLogger.info('packing process started')
    sch = schema.getBackupSchema(schemaName)
    
    ignore = sch.get('ignore', '')

    if not sch: 
        programLogger.fatal(f'packing process failed: no schema "{schemaName}"')
        exit(1)
    
    tmp = getTMP()

    archive = tarfile.open(os.path.join(tmp, f'{schemaName}.tar'), 'w')
    
    if not sch.get('targets'):
        programLogger.fatal(f'failed to get "targets" key from schema "{schemaName}"')
        exit(1)

    packedCount = 0
    packedTargets = []
    result = {
        'files':0,
        'ignored': 0,
        'size': 0,
        'scannedSize': 0
    }
    res:dict
    packFile.counter = 0
    packFolder.counter = 0
    for target in sch['targets']:
        if os.path.isfile(target):
            res = packFile(target, archive)
        else:
            res = packFolder(target, archive, ignore)

        if res:
            packedTargets.append(target)
            for k in res.keys():
                result[k] += res[k]
            packedCount += 1

    configurePack(archive, sch, packedTargets)

    programLogger.info(f'packing process finished successfully;\n'
                       f' - packs created: {packedCount}/{len(sch["targets"])}\n'
                       f' - archived and ignored total files: {result['files']}/{result['ignored']}\n'
                       f' - archived total size: {result["size"]}/{result["scannedSize"]}'
                       )
    archive.close()


def packFolder(targetFolder:str, archive:tarfile.TarFile, ignore:str):
    if not os.path.exists(targetFolder):
        programLogger.error(f'packing failed: target folder "{targetFolder}" not exists')
        return

    programLogger.info(f'packing target folder "{targetFolder}"; reading content...')
    files = []
    scanned = 0
    ignored = 0
    scannedSize = 0
    packSize = 0

    GLOBAL = ' __global__ '
    specs = {GLOBAL: pathspec.PathSpec.from_lines('gitignore', ignore.splitlines())}
    specsPaths = [GLOBAL]

    for dpath, _, fnames in os.walk(targetFolder):
        spec = loadIgnorePatterns(dpath)
        if spec:
            specs[dpath] = spec
            specsPaths = sorted(specs.keys(), key=len, reverse=False)

        for fname in fnames:
            relative_path = os.path.relpath(os.path.join(dpath, fname), targetFolder)
            if not shouldIgnore(os.path.join(dpath, fname), specs, specsPaths):
                files.append(relative_path)
            else:
                ignored += 1

            scannedSize += os.path.getsize(os.path.join(targetFolder, relative_path))
            scanned += 1

    ignored += len(files)
    files  = [p for p in files if not specs[GLOBAL].match_file(p)]
    ignored -= len(files)
    for p in files:
        packSize += os.path.getsize(os.path.join(targetFolder, p))

    programLogger.info(f'reading success; total files: {len(files)} [{packSize}B/{scannedSize}B]; ignored total: {ignored}')    

    programLogger.info(f'adding to archive...')
    
    for f in files:
        dpath = os.path.join(f'folders/{hex(packFolder.counter)[2:]}',f)
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

    size = os.path.getsize(targetFile)

    archive.add(targetFile, f'files/{hex(packFile.counter)[2:]}')
    packFile.counter += 1
    return {
        'files': 1,
        'ignored': 0,
        'size': size,
        'scannedSize': size
    }


def configurePack(archive:tarfile.TarFile, backupSchema:dict, packedTargets:list):
    programLogger.info('configuring pack...')

    if not backupSchema.get('destination'):
        programLogger.fatal(f'failed to get "destination" param from schema')
        exit(1)

    data = {
        'creation-time': time.time(),
        'destination': backupSchema['destination'],
        'files': [p for p in packedTargets if os.path.isfile(p)],
        'folders': [p for p in packedTargets if os.path.isdir(p)]
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


def unpackFile(path:str, index:int, archive:tarfile.TarFile):
    programLogger.info(f'unpacking file "{path}"...')

    if not os.path.exists(os.path.dirname(path)):
        programLogger.error(f'failed to unpack because "{os.path.dirname(path)}" not exists')
        return
    
    if os.path.exists(path) and not Config().allow_local_replace:
        path = os.path.join(os.path.dirname(path), os.path.basename(path) + '-restored')

    member = archive.getmember(f'files/{hex(index)[2:]}')

    rewritten = os.path.exists(path)
    
    with archive.extractfile(member) as file_obj:
        with open(path, 'wb') as out_file:
            out_file.write(file_obj.read())

    programLogger.info(f'success! unpacked to "{path}"')
    return {
        'rewritten': rewritten,
        'restored': not rewritten
    }


def unpackFolder(path:str, index:int, archive:tarfile.TarFile):
    programLogger.info(f'unpacking folder "{path}"...')
    
    if not os.path.exists(os.path.dirname(path)):
        programLogger.error(f'failed to unpack because "{os.path.dirname(path)}" not exists')
        return
    
    if os.path.exists(path) and not Config().allow_local_replace:
        path = os.path.join(os.path.dirname(path), os.path.basename(path) + '-restored')
        if os.path.exists(path):
            os.rmdir(path)
        os.mkdir(path)
    elif not os.path.exists(path):
        os.mkdir(path)

    rewrittenCount = 0
    restoredCount = 0

    for member in archive.getmembers():
        memberRoot = f'folders/{hex(index)[2:]}'
        if not (member.name.startswith(memberRoot) and member.isfile()):
            continue

        relpath = os.path.relpath(member.name, memberRoot)
        targetFilePath = os.path.join(path, relpath)

        if os.path.exists(targetFilePath):
            rewrittenCount += 1
        else:
            restoredCount += 1

        os.makedirs(os.path.dirname(targetFilePath), exist_ok=True)

        with archive.extractfile(member) as file_obj:
            with open(targetFilePath, 'wb') as out_file:
                out_file.write(file_obj.read())

    programLogger.info(f'success! unpacked to "{path}"\n'
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
    
    if Config().allow_local_replace and Config().ask_before_replace:
        print(f'{LYC}Are you sure to rewrite next folders and files:')
        for f in packConfig['folders']:
            print(f'{LYC} - {f}')
        for f in packConfig['files']:
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
    i = 0
    for folder in packConfig['folders']:
        res = unpackFolder(folder, i, archive)

        result['rewritten'] += res['rewritten']
        result['restored'] += res['restored']
        i += 1
    i = 0
    for file in packConfig['files']:
        res = unpackFile(file, i, archive)

        result['rewritten'] += res['rewritten']
        result['restored'] += res['restored']
        i += 1

    programLogger.info(f'unpacking finished with success!\n'
                       f' - rewritten total: {result['rewritten']}\n'
                       f' - restored total: {result["restored"]}')
    archive.close()
