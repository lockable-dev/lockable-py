import concurrent.futures
import datetime as dt
import logging
import time

from . import client

log = logging.getLogger(__name__)

HEARTBEAT_SLEEP = dt.timedelta(milliseconds=1000)
ACQUIRE_SLEEP = dt.timedelta(milliseconds=1000)


class Lock:
		"""
		Usage:
		```
		with Lock('my_lock_name'):
				#do stuff
		```
		"""

		# TODO: Handle cases where lockable.dev is down
		# TODO: make sleep periods configurable
		def __init__(self, lock_name, on_heartbeat_failure=None, blocking=True):
				self.lock_name = lock_name
				self.on_heartbeat_failure = on_heartbeat_failure
				self._blocking = blocking

		def _block_and_acquire(self):
				"""
				Attempt to acquire the lock from lockable.dev.
				If the lock is not available and self._blocking is True,
				then periodically reattempt to acquire the lock
				If self._blocking is False, raise CouldNotAcquireLockError
				"""
				while True:
						acquire_response = client.try_acquire(self.lock_name)
						if acquire_response:
								return
						if not self._blocking:
								raise CouldNotAcquireLockError(self.lock_name)
						time.sleep(ACQUIRE_SLEEP.total_seconds())

		def acquire(self):
				self._block_and_acquire()
				self._release_lock_flag = False
				self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
				log.debug("Starting heartbeat loop")
				# TODO: Handle errors in hb threads; currently, the errors are swalloed
				self._executor.submit(self._run_heartbeat_loop)
				log.debug("Heartbeat loop started")

		def release(self):
				self._release_lock_flag = True
				client.try_release()
				self._executor.shutdown()

		def __enter__(self):
				self.acquire()

		def __exit__(self, exc_type, exc_value, exc_tb):
				# TODO: Handle errors
				self.release()

		def _run_heartbeat_loop(self):
				while True:
						if self._release_lock_flag:
								return
						heartbeat_response = client.try_heartbeat()
						if heartbeat_response is False:
								# We've lost the lock
								# Use the callback to notify the main thread
								self.on_heartbeat_failure()
								return
						time.sleep(HEARTBEAT_SLEEP.total_seconds())


class CouldNotAcquireLockError(Exception):
		pass
