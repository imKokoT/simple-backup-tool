from core.app_config import config
from core.context import ctx


def scan():
    args = ctx.args
    schema = ctx.schema

    ignore = schema.get('ignore')
    targets = schema.get('targets')

    
