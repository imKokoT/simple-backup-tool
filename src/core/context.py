from argparse import Namespace, ArgumentParser, _SubParsersAction

import time
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.module import Chain, Module
    from core.schema import Schema


class Context:
    """Stores runtime data"""
    sessionTime = time.ctime() 

    # cli
    args:Namespace
    parser:ArgumentParser
    subparsers:_SubParsersAction[ArgumentParser]

    # module
    currentModule:Module = None # NOTE: if 'None' here, may you forgot to run module through invoke()
    chains:list[Chain]
    schema:Schema

ctx = Context()
