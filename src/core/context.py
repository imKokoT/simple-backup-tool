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
    schema:Schema

    currentModule:Module    # NOTE: if 'None' here, may you forgot to add super().run() at your module
    chains:list[Chain]

ctx = Context()
