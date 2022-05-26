import logging
import time
import uuid

from lockable import Lock

log = logging.getLogger(__name__)


def test_lock(caplog):
    caplog.set_level(logging.DEBUG, logger='lockable.lock')
    caplog.set_level(logging.DEBUG, logger='lockable.client')
    caplog.set_level(logging.DEBUG, logger=__name__)
    with Lock(str(uuid.uuid4())):
        log.debug('In with statement')
        time.sleep(5)
        pass
    return
