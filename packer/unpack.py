import tarfile
from config import *
from miscellaneous import getTMP, getFolderPath
from packer.packconfig import loadPackConfig
from packer.tools import dumpRestoredLog, modifyRestorePaths, modifySingleRestorePath


def invalidTargetPathHandle(path, schema, packConfig) -> str:
    if not Config().ask_for_other_extract_path and not Config().restore_to_tmp_if_path_invalid: 
        programLogger.error(f'failed to unpack because "{os.path.dirname(path)}" not exists')
        return
    elif Config().restore_to_tmp_if_path_invalid and not Config().ask_for_other_extract_path:
        programLogger.warning(f'{os.path.dirname(path)} is invalid! files will be restored to tmp/restored')
        path = modifySingleRestorePath(path, schema, packConfig, False)
    else:
        print(f'{YC}Path "{path}" is invalid, do you want to unpack to other path?')
        newDir = getFolderPath()
        if not newDir:
            if not Config().restore_to_tmp_if_path_invalid:
                programLogger.info(f'skipped')
                return
            
            path = modifySingleRestorePath(path, schema, packConfig, False)
        else:
            path = os.path.join(newDir.strip(), os.path.basename(path))

    return path


def unpackFile(path:str, index:int, archive:tarfile.TarFile, schema:dict, packConfig:dict):
    programLogger.info(f'unpacking file "{path}"...')

    if not os.path.exists(os.path.dirname(path)):
        path = invalidTargetPathHandle(path, schema, packConfig)
    
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


def unpackFolder(path:str, index:int, archive:tarfile.TarFile, schema:dict, packConfig:dict):
    programLogger.info(f'unpacking folder "{path}"...')
    
    if not os.path.exists(os.path.dirname(path)):
        path = invalidTargetPathHandle(path, schema, packConfig)
    
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
    os.makedirs(f'{tmp}/restored/{schemaName}', exist_ok=True)
    archive = tarfile.open(os.path.join(tmp, f'{schemaName}.tar'), 'r')

    packConfig = loadPackConfig(archive)

    dumpRestoredLog(packConfig, schema)
    
    if Config().allow_local_replace and Config().ask_before_replace:
        print(f'{LYC}Are you sure to rewrite next folders and files:')
        for f in packConfig['folders']:
            print(f'{LYC} - {f}')
        for f in packConfig['files']:
            print(f'{LYC} - {f}')
        yn = input('[y/N] ')
        if yn.strip().lower() != 'y':
            print('restored data placed in tmp folder')
            print(f'{LYC}do you want to unpack all to "{tmp}/restored/{schemaName}":')
            yn = input('[y/N] ')
            if yn.strip().lower() == 'y':
                modifyRestorePaths(packConfig, schema)
            else:
                print('unpack process interrupted...')
                exit(0)

    result = {
        'rewritten': 0,
        'restored': 0
    }
    res:dict
    i = 0
    for folder in packConfig['folders']:
        res = unpackFolder(folder, i, archive, schema, packConfig)
        
        if res:
            result['rewritten'] += res['rewritten']
            result['restored'] += res['restored']
        i += 1
    i = 0
    for file in packConfig['files']:
        res = unpackFile(file, i, archive, schema, packConfig)

        if res:
            result['rewritten'] += res['rewritten']
            result['restored'] += res['restored']
        i += 1

    programLogger.info(f'unpacking finished with success!\n'
                       f' - rewritten total: {result['rewritten']}\n'
                       f' - restored total: {result["restored"]}')
    archive.close()
