from . import authenticate
from . import drive
from . import clean


def getStorageQuota(service) -> dict:
    quota = service.about().get(fields='storageQuota').execute()['storageQuota']
    return {k: int(v) for k, v in quota.items()}
