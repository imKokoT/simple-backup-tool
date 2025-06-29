import os
import fnmatch
import yaml
import pathspec
import platform
from yaml.scanner import ScannerError
from properties import *
from logger import logger
from runtime_data import rtd


def getBackupSchema(schemaName:str, skipUnwrap:bool = False) ->dict|None:
    schema = None

    if not os.path.exists('configs/schemas'):
        os.mkdir('configs/schemas')

    schemas = [p for p in os.listdir('configs/schemas') if fnmatch.fnmatch(p, '*.yml') or fnmatch.fnmatch(p, '*.yaml')]
    schemasNames = [os.path.basename(p.split('.')[0]) for p in schemas]
    if schemaName not in schemasNames:
        return None
    
    # recursion check
    if not skipUnwrap:
        rtd.push('_include-chain', [schemaName])
    else:
        if schemaName in rtd['_include-chain']:
            rtd['_include-chain'].append(schemaName)
            logger.critical(f'found recursive including of schema template "{schemaName}"; chain: {'/'.join(rtd['_include-chain'])}') # type: ignore
            exit(1)
        else:
            rtd['_include-chain'].append(schemaName)

    schema = load(f'configs/schemas/{schemas[schemasNames.index(schemaName)]}', skipUnwrap)

    assert schema.get('__name__') if schema else True, f'Loaded schema "{schemaName}" has not the "__name__" key!'

    rtd.push('schema', schema, overwrite=True)
    return schema


def filterSimplePaths(paths) -> set:
    return {p for p in paths if not any(char in p for char in '!*?[]')}


def unwrapTargets(schema:dict):
    if not schema.get('targets'):
        return
    
    paths = filterSimplePaths(schema['targets'])
    patterns = [p for p in schema['targets'] if p not in paths]
    
    if len(patterns):
        logger.info('unwrapping targets')
    else:
        return
    
    for pattern in patterns:
        logger.debug(f'unwrapping "{pattern}"')
        preroot = pattern.split('/')
        root = []
        for part in preroot:
            if any(char in part for char in '!*?[]'):
                break
            root.append(part)
        root = '/'.join(root)
        spec = pathspec.PathSpec.from_lines('gitwildmatch', [pattern[len(root):]])

        tree = spec.match_tree(root)
        exp = [f'{root}/{p}' for p in tree]
        paths.update(exp)
        logger.debug(f'unwrapped {len(exp)} targets')
    
    schema['targets'] = list(paths)


def load(fpath:str, skipUnwrap:bool = False) -> dict:
    logger.debug(f'loading schema "{fpath}"')
    if not os.path.exists(fpath):
        logger.fatal(f'failed to load schema "{fpath}" because in not exists')
        exit(1)    

    with open(fpath, 'r', encoding='utf-8') as f:
        try:
            schema = yaml.safe_load(f)
        except ScannerError as e:
            logger.fatal(f'schema from path "{fpath}" has bad format! Error:\n{e}')
            exit(1)

    if type(schema) is not dict:
        logger.fatal(f'schema from path "{fpath}" has wrong format! It must be dict-like.')
        exit(1)

    if schema:
        schema['__name__'] = os.path.basename(fpath).split('.')[0]
        logger.debug(f'processing "{schema["__name__"]}" keys')

        # handle target is multiline string format
        if type(schema.get('targets')) is str:
            schema['targets'] = [p.strip() for p in schema['targets'].split('\n') if p.strip() != ''] # type: ignore
        # handle ~ alias
        if platform.system() == 'Linux' and schema.get('targets'):
            home = os.getenv('HOME')
            schema['targets'] = [p.replace('~', home) for p in schema['targets']]

        if not skipUnwrap:
            unwrapTargets(schema)

        if schema.get('include'):
            schema = include(schema, schema.get('include'))
    
    logger.debug(f'postprocessing "{schema["__name__"]}" keys')
    # detect encryption
    if schema.get('encryption'):
        if not schema.get('password') and not schema.get('_enc_keyword'):
            logger.fatal(f'encryption enabled, "password" parameter required!')
            exit(1)
        if not schema.get('_enc_keyword'):
            logger.debug('encryption detected')
            schema['_enc_keyword'] = schema.pop('password')
        elif schema.get('password'):
            schema.pop('password')
    
    return schema


def include(schema:dict, include:str) -> dict:
    logger.debug(f'trying to include schema "{include}"')
    t = getBackupSchema(include, True)
    if not t:
        logger.fatal(f'failed to include "{include}" for "{schema['__name__']}", because it not exists')
        exit(1)
    
    logger.debug(f'updating keys')
    for k, v in t.items():
        if schema.get(k):
            continue
        schema[k] = v
    
    return schema
