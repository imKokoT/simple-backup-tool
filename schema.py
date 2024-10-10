import os
import yaml
from config import *


def include(schema:dict, include:str) -> dict:
    t = getBackupSchema(include)
    if not t:
        programLogger.fatal(f'failed to include "{include}" for "{schema['__name__']}", because it not exists')
        exit(1)
    
    for k, v in t.items():
        if schema.get(k):
            continue
        schema[k] = v
    
    return schema


def getBackupSchema(schemaName:str) ->dict|None:
    if not os.path.exists('./configs/schemas.yaml'):
        return None
    
    data:dict
    with open('./configs/schemas.yaml', 'r') as f:
        data = yaml.safe_load(f)

    schema = data.get(schemaName)
    if schema:
        schema['__name__'] = schemaName
        if schema.get('include'):
            return include(schema, schema.get('include'))

    return schema
