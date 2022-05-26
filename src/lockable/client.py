import logging

import requests as rq

log = logging.getLogger(__name__)

LOCKABLE_DOMAIN = "api.lockable.dev"


def try_acquire(lock_name, auth_token=None):
    log.debug(f"Attempting to acquire lock: {lock_name}")
    auth = (auth_token, '') if auth_token else None
    res = rq.get(f"https://{LOCKABLE_DOMAIN}/v1/acquire/{lock_name}", auth=auth)
    res.raise_for_status()
    response = res.json()["response"]
    log.debug(f"Lock acquision for {lock_name}: {response}")
    return response


def try_heartbeat(lock_name, auth_token=None):
    log.debug(f"Attempting to heartbeat lock: {lock_name}")
    auth = (auth_token, '') if auth_token else None
    res = rq.get(f"https://{LOCKABLE_DOMAIN}/v1/heartbeat/{lock_name}", auth=auth)
    res.raise_for_status()
    response = res.json()["response"]
    log.debug(f"Lock heartbeat for {lock_name}: {response}")
    return response


def try_release(lock_name, auth_token=None):
    log.debug(f"Attempting to release lock: {lock_name}")
    auth = (auth_token, '') if auth_token else None
    res = rq.get(f"https://{LOCKABLE_DOMAIN}/v1/release/{lock_name}", auth=auth)
    res.raise_for_status()
    log.debug(f"Lock released for {lock_name}")
