import os
import fnmatch
import yaml
from yaml.scanner import ScannerError
from config import *


def include(schema:dict, include:str) -> dict:
    t = getBackupSchema(include)
    if not t:
        logger.fatal(f'failed to include "{include}" for "{schema['__name__']}", because it not exists')
        exit(1)
    
    for k, v in t.items():
        if schema.get(k):
            continue
        schema[k] = v
    
    return schema


def getBackupSchema(schemaName:str) ->dict|None:
    data:dict
    schema = None

    if not schema:
        if not os.path.exists('configs/schemas'):
            os.mkdir('configs/schemas')

        schemas = [p for p in os.listdir('configs/schemas') if fnmatch.fnmatch(p, '*.yml') or fnmatch.fnmatch(p, '*.yaml')]
        schemasNames = [os.path.basename(p.split('.')[0]) for p in schemas]
        if schemaName not in schemasNames:
            return None

        schema = load(f'configs/schemas/{schemas[schemasNames.index(schemaName)]}')

    return schema


def load(fpath:str) -> dict:
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
        if schema.get('include'):
            return include(schema, schema.get('include'))

    return schema
