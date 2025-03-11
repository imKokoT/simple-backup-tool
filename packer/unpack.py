import os
import tarfile
from app_config import Config
from properties import *
from miscellaneous.miscellaneous import getTMP, getFolderPath
from packer.packconfig import loadPackConfig
from packer.tools import dumpRestoredLog, modifyRestorePaths, modifySingleRestorePath
from logger import logger
from runtime_data import rtd


def unpackAll():
    logger.info('unpacking process started')
    
    schema:dict = rtd['schema']
    tmp = getTMP()
    schemaName = schema['__name__']
    os.makedirs(f'{tmp}/restored/{schemaName}', exist_ok=True)
    archive = tarfile.open(os.path.join(tmp, f'{schemaName}.tar'), 'r')

    packConfig = loadPackConfig(archive)

    dumpRestoredLog(packConfig)
    
    if Config().allow_local_replace and Config().ask_before_replace:
        askForLocalReplace(packConfig)

    result = {
        'rewritten': 0,
        'restored': 0
    }
    res:dict
    i = 0
    for folder in packConfig['folders']:
        res = unpackFolder(folder, i, archive, packConfig)
        
        if res:
            result['rewritten'] += res['rewritten']
            result['restored'] += res['restored']
        i += 1
    i = 0
    for file in packConfig['files']:
        res = unpackFile(file, i, archive, packConfig)

        if res:
            result['rewritten'] += res['rewritten']
            result['restored'] += res['restored']
        i += 1

    logger.info(f'unpacking finished with success!\n'
                       f' - rewritten total: {result['rewritten']}\n'
                       f' - restored total: {result["restored"]}')
    archive.close()


def unpackFile(path:str, index:int, archive:tarfile.TarFile, packConfig:dict):
    logger.info(f'unpacking file "{path}"...')
    schema:dict = rtd['schema']

    if not os.path.exists(os.path.dirname(path)):
        path = invalidTargetPathHandle(path, packConfig)
    
    if os.path.exists(path) and not Config().allow_local_replace:
        path = os.path.join(os.path.dirname(path), os.path.basename(path) + '-restored')

    member = archive.getmember(f'files/{hex(index)[2:]}')

    rewritten = os.path.exists(path)
    
    with archive.extractfile(member) as file_obj: # type: ignore
        with open(path, 'wb') as out_file:
            out_file.write(file_obj.read())

    logger.info(f'success! unpacked to "{path}"')
    return {
        'rewritten': rewritten,
        'restored': not rewritten
    }


def unpackFolder(path:str, index:int, archive:tarfile.TarFile, packConfig:dict):
    logger.info(f'unpacking folder "{path}"...')
    schema:dict = rtd['schema']

    if not os.path.exists(os.path.dirname(path)):
        path = invalidTargetPathHandle(path, packConfig)

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

        with archive.extractfile(member) as file_obj: # type: ignore
            with open(targetFilePath, 'wb') as out_file:
                out_file.write(file_obj.read())

    logger.info(f'success! unpacked to "{path}"\n'
                       f' - rewritten: {rewrittenCount}\n'
                       f' - restored: {restoredCount}')
    return {
        'rewritten': rewrittenCount,
        'restored': restoredCount
    }


def askForLocalReplace(packConfig):
    tmp = getTMP()
    schema:dict = rtd['schema']
    schemaName = schema['__name__']

    print(f'{LYC}Are you sure to rewrite next folders and files:')
    for f in packConfig['folders']:
        print(f'{LYC} - {f}')
    for f in packConfig['files']:
        print(f'{LYC} - {f}')
    yn = input('[y/N] ')
    if yn.strip().lower() != 'y':
        print(f'{LYC}do you want to unpack all to "{tmp}/restored/{schemaName}":')
        yn = input('[y/N] ')
        if yn.strip().lower() == 'y':
            logger.info('restored data placed in tmp/restored folder')
            modifyRestorePaths(packConfig)
        else:
            print('unpack process interrupted...')
            exit(0)


def invalidTargetPathHandle(path, packConfig) -> str:
    schema:dict = rtd['schema']

    if not Config().ask_for_other_extract_path and not Config().restore_to_tmp_if_path_invalid: 
        logger.error(f'failed to unpack because "{os.path.dirname(path)}" not exists')
        return
    elif Config().restore_to_tmp_if_path_invalid and not Config().ask_for_other_extract_path:
        logger.warning(f'{os.path.dirname(path)} is invalid! files will be restored to tmp/restored')
        path = modifySingleRestorePath(path, packConfig, False)
    else:
        print(f'{YC}Path "{path}" is invalid, do you want to unpack to other path?')
        newDir = getFolderPath()
        if not newDir:
            if not Config().restore_to_tmp_if_path_invalid:
                logger.info(f'skipped')
                return
            
            path = modifySingleRestorePath(path, packConfig, False)
        else:
            path = os.path.join(newDir.strip(), os.path.basename(path))

    return path
