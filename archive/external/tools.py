import sys
import subprocess
from logger import logger


def run(program:str, command:list):
    try:
        result = subprocess.run(command, text=True, stdout=sys.stdout)
    except FileNotFoundError:
        logger.fatal(f'program "{program}" not found')
        exit(1)

    if result.returncode == 0:
        logger.info("compress finished with success!")
    else:
        logger.fatal(f"external process error: {result.stderr}")
        exit(1)
