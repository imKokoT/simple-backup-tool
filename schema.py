import os
import yaml


def getBackupSchema(schemaName:str) ->dict|None:
    if not os.path.exists('./configs/schemas.yaml'):
        return None
    
    data:dict
    with open('./configs/schemas.yaml', 'r') as f:
        data = yaml.safe_load(f)

    schema = data.get(schemaName)
    return schema
