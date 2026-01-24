from argparse import Namespace
from core.module import Chain
from core.schema import Schema


class Context:
    """Stores runtime data"""
    args:Namespace
    schema:Schema

    chains:list[Chain]

ctx = Context()
