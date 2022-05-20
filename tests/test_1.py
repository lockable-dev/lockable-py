from lockable import Lock
import logging
import time
import uuid

log = logging.getLogger(__name__)


def test_lock(caplog):
    caplog.set_level(logging.DEBUG, logger='lockable.lock')
    caplog.set_level(logging.DEBUG, logger='lockable.client')
    caplog.set_level(logging.DEBUG, logger=__name__)
    with Lock(str(uuid.uuid4())) as l:
        log.debug('In with statement')
        time.sleep(5)
        pass
    return
