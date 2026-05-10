from argparse import Namespace

import time
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.module import Chain, Module
    from core.schema import Schema


class Context:
    """Stores runtime data"""
    sessionTime = time.ctime() 
    args:Namespace

    currentModule:Module = None # NOTE: if 'None' here, may you forgot to run module through invoke()
    chains:list[Chain]
    schema:Schema

ctx = Context()
