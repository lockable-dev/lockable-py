from lockable import Lock, hello
import logging
import time

log = logging.getLogger(__name__)


def test_lock(caplog):
		caplog.set_level(logging.DEBUG, logger='lockable.lockable')
		caplog.set_level(logging.DEBUG, logger=__name__)
		import uuid
		with Lock(str(uuid.uuid4())) as l:
				log.debug('In with statement')
				time.sleep(5)
				pass
		return
