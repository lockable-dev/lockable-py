import concurrent.futures
import datetime as dt
import logging
import threading
import time
from contextlib import contextmanager

from . import client
from .exceptions import CouldNotAcquireLockError

log = logging.getLogger(__name__)

DEFAULT_HEARTBEAT_SLEEP_PERIOD = dt.timedelta(milliseconds=1000)
DEFAULT_ACQUIRE_SLEEP_PERIOD = dt.timedelta(milliseconds=1000)


class Lock:
    """
    Usage:
    ```
    with Lock('my_lock_name'):
        #do stuff
    ```
    """

    def __init__(
        self,
        lock_name,
        blocking=True,
        on_lock_loss=lambda: None,
        on_heartbeat_exception=lambda e: None,
        acquire_sleep_period=DEFAULT_ACQUIRE_SLEEP_PERIOD,
        heartbeat_sleep_period=DEFAULT_HEARTBEAT_SLEEP_PERIOD,
    ):
        self.lock_name = lock_name
        self._blocking = blocking
        self._heartbeat_loop = HeartBeatLoop(
            lock=self,
            on_lock_loss=on_lock_loss,
            on_heartbeat_exception=on_heartbeat_exception,
            heartbeat_sleep_period=heartbeat_sleep_period,
        )
        self._acquire_sleep_period = acquire_sleep_period

    def _maybe_block_and_acquire(self):
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
            time.sleep(self._acquire_sleep_period.total_seconds())

    def acquire(self):
        self._maybe_block_and_acquire()
        self._heartbeat_loop.start()

    def release(self):
        client.try_release(self.lock_name)
        self._heartbeat_loop.shutdown()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.release()

    def __repr__(self):
        return f"Lock({repr(self.lock_name)}, blocking={repr(self._blocking)})"


class HeartBeatLoop:
    def __init__(
        self,
        lock,
        on_lock_loss,
        on_heartbeat_exception,
        heartbeat_sleep_period,
    ):
        self._lock = lock
        # The hb thread will hold the _interrupt_lock whenever it is in a state
        # where it does not want to be interrupted
        # e.g. processing an exception callback
        # Used via self._interruptable and self._not_interruptable
        # context managers
        self._interrupt_lock = threading.Lock()
        self._on_lock_loss = on_lock_loss
        self._on_heartbeat_exception = on_heartbeat_exception
        self._heartbeat_sleep_period = heartbeat_sleep_period
        self._shutdown_requested = False

    def start(self):
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        log.debug("Starting heartbeat loop")
        self._executor.submit(self._run_heartbeat_loop)
        log.debug("Heartbeat loop started")

    def shutdown(self):
        log.debug("Shutting down heartbeat loop")
        self._shutdown_requested = True
        self._executor.shutdown()
        self._shutdown_requested = False
        log.debug("Heartbeat loop shut down")

    def _run_heartbeat_loop(self):
        """
        This function runs on the heartbeat thread.
        Any threading issues can only appear by interleaving this code
        with the rest of the code running on the main thread.

        To avoid race conditions we use self._interruptable
        and self._not_interruptable to mark potions of the code
        where the loop can be interrupted by self._executor.shutdown()
        """
        self._loop_error = None
        try:
            while not self._shutdown_requested:
                heartbeat_response = client.try_heartbeat(self._lock.lock_name)
                if heartbeat_response is False:
                    # We've lost the lock
                    # Use the callback to notify the main thread
                    log.debug("Entering _on_lock_loss")
                    self._on_lock_loss()
                    log.debug("Leaving _on_lock_loss")
                    return
                time.sleep(self.heartbeat_sleep_period.total_seconds())
        except Exception as e:
            # Something went wrong
            # Use the exception callback to notify the main thread
            log.debug("Entering _on_heartbeat_exception")
            self._on_heartbeat_exception(e)
            log.debug("Leaving _on_heartbeat_exception")
            self._loop_error = e
