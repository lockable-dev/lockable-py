import datetime as dt
import logging
import os
import time
import uuid

import pytest
import requests

from lockable import Lock


def test_auth_fail(caplog):
    caplog.set_level(logging.DEBUG, logger='lockable.lock')
    caplog.set_level(logging.DEBUG, logger='lockable.client')
    caplog.set_level(logging.DEBUG, logger=__name__)

    os.environ = {'LOCKABLE_AUTH_TOKEN': 'bad_token'}
    with pytest.raises(requests.exceptions.HTTPError):
        with Lock(
                lock_name=uuid.uuid4(),
                heartbeat_sleep_period=dt.timedelta(milliseconds=100),
                acquire_sleep_period=dt.timedelta(milliseconds=100)
                ):
            time.sleep(dt.timedelta(milliseconds=500).total_seconds())


def test_auth_pass(caplog):
    caplog.set_level(logging.DEBUG, logger='lockable.lock')
    caplog.set_level(logging.DEBUG, logger='lockable.client')
    caplog.set_level(logging.DEBUG, logger=__name__)

    os.environ = {'LOCKABLE_AUTH_TOKEN': '570b7766-c7d5-402b-961e-d751d7afaaa3'}
    lock_name = uuid.uuid4()
    with Lock(
            lock_name=lock_name,
            heartbeat_sleep_period=dt.timedelta(milliseconds=100),
            acquire_sleep_period=dt.timedelta(milliseconds=100)
            ):
        time.sleep(dt.timedelta(milliseconds=500).total_seconds())
