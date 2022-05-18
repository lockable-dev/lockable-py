import concurrent.futures
import datetime as dt
import logging
import time

from . import client

log = logging.getLogger(__name__)

HEARTBEAT_SLEEP = dt.timedelta(milliseconds=1000)
ACQUIRE_SLEEP = dt.timedelta(milliseconds=1000)

HB_STOPPED = "STOPPED"
HB_RUNNING = "RUNNING"
HB_ERROR = "ERROR"


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
    def __init__(
        self,
        lock_name,
        blocking=True,
        on_heartbeat_failure=lambda: None,
        on_heartbeat_exception=lambda x: None,
    ):
        self.lock_name = lock_name
        self._blocking = blocking
        self.on_heartbeat_failure = on_heartbeat_failure
        self.on_heartbeat_exception = on_heartbeat_exception
        # this should only be set by the threading code
        # and read by the main code
        self._hb_thread_status = HB_STOPPED
        # this should only be set by the main code
        # and read by the threading code
        self._release_lock_flag = False

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
        self._release_lock_flag = False
        self._block_and_acquire()
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        log.debug("Starting heartbeat loop")
        self._executor.submit(self._run_heartbeat_loop)
        log.debug("Heartbeat loop started")

    def release(self):
        self._release_lock_flag = True
        client.try_release(self.lock_name)
        self._executor.shutdown()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        # TODO: Handle errors
        self.release()

    def _run_heartbeat_loop(self):
        """
        This function runs on the heartbeat thread.
        Any threading issues can only appear by interleaving this code
        with the rest of the code running on the main thread
        """
        self._hb_thread_status = HB_RUNNING
        try:
            while True:
                if self._release_lock_flag:
                    self._hb_thread_status = HB_STOPPED
                    return
                heartbeat_response = client.try_heartbeat(self.lock_name)
                if heartbeat_response is False:
                    # We've lost the lock
                    # Use the callback to notify the main thread
                    self._hb_thread_status = HB_STOPPED
                    self.on_heartbeat_failure()
                    return
                time.sleep(HEARTBEAT_SLEEP.total_seconds())
        except Exception as e:
            self.on_heartbeat_exception(e)
            self._hb_thread_status = (HB_ERROR, e)

    def __repr__(self):
        return f'Lock({repr(self.lock_name)}, blocking={repr(self._blocking)})'


class CouldNotAcquireLockError(Exception):
    pass
