import concurrent.futures
import datetime as dt
import logging
import random
import time
import uuid

from lockable import Lock


def test_load_one(caplog):
    caplog.set_level(logging.DEBUG, logger='lockable.lock')
    caplog.set_level(logging.DEBUG, logger='lockable.client')
    caplog.set_level(logging.DEBUG, logger=__name__)

    with Lock(
            lock_name=uuid.uuid4(),
            heartbeat_sleep_period=dt.timedelta(milliseconds=100),
            acquire_sleep_period=dt.timedelta(milliseconds=100)
            ):
        time.sleep(dt.timedelta(milliseconds=500).total_seconds())


def test_load(caplog):
    caplog.set_level(logging.DEBUG, logger='lockable.lock')
    caplog.set_level(logging.DEBUG, logger='lockable.client')
    caplog.set_level(logging.DEBUG, logger=__name__)

    random.seed(a=1337)
    min_delay_ms = 0
    max_delay_ms = 1000
    min_duration_ms = 0
    max_duration_ms = 1500
    N = 400
    M = 4

    lock_names = [uuid.uuid4() for _ in range(M)]
    local_locks = {l: False for l in lock_names}
    processes = []
    for _ in range(N):
        delay_ms = random.randrange(min_delay_ms, max_delay_ms)
        delay = dt.timedelta(milliseconds=delay_ms)
        duration_ms = random.randrange(min_duration_ms, max_duration_ms)
        duration = dt.timedelta(milliseconds=duration_ms)
        lock_name = random.choice(lock_names)
        process = Process(delay, duration, lock_name, local_locks)
        processes.append(process)

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=N)
    tasks = []
    for process in processes:
        future = executor.submit(process.run)
        tasks.append((process, future))
    assert all(_[1].result() is None for _ in tasks)


class Process:
    def __init__(self, delay, duration, lock_name, local_locks):
        self._delay = delay
        self._duration = duration
        self._lock_name = lock_name
        self._local_locks = local_locks

    def run(self):
        try:
            time.sleep(self._delay.total_seconds())
            with Lock(
                    self._lock_name,
                    heartbeat_sleep_period=dt.timedelta(milliseconds=100),
                    acquire_sleep_period=dt.timedelta(milliseconds=100)
                    ):
                assert self._local_locks[self._lock_name] is False
                self._local_locks[self._lock_name] = True
                time.sleep(self._duration.total_seconds())
                assert self._local_locks[self._lock_name] is True
                self._local_locks[self._lock_name] = False
        except Exception as e:
            return e

    def __repr__(self):
        return f'Process({repr(self._delay)}, {repr(self._duration)}, {repr(self._lock_name)})'
