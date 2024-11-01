import os
import fnmatch
import yaml
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

    if os.path.exists('./configs/schemas.yaml'):
        with open('./configs/schemas.yaml', 'r') as f:
            data = yaml.safe_load(f)    
        schema = data.get(schemaName)
    
    if not schema:
        if not os.path.exists('configs/schemas'):
            os.mkdir('configs/schemas')

        schemas = [p for p in os.listdir('configs/schemas') if fnmatch.fnmatch(p, '*.yml') or fnmatch.fnmatch(p, '*.yaml')]
        schemasNames = [os.path.basename(p.split('.')[0]) for p in schemas]
        if schemaName not in schemasNames:
            return None

        with open(f'configs/schemas/{schemas[schemasNames.index(schemaName)]}', 'r') as f:
            schema = yaml.safe_load(f)

    if schema:
        schema['__name__'] = schemaName
        if schema.get('include'):
            return include(schema, schema.get('include'))

    return schema
