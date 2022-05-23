# Lockable-dev
Official Python client for https://lockable.dev

Lockable is an easy-to-use, language-independent locking mechanism for multi-process workloads. Think of it as `flock`, but for distributed systems which may not be sharing a filesystem.


## Installation
```
pip install lockable-dev
```


## Usage
```
from lockable import Lock
with Lock('my-lock-name'):
    #do stuff
```
This will guarantee your process will only enter the `with` block if the `'my-lock-name'` can be acquired. It will block otherwise until it can acquire the lock.

The lock is held for as long as the process is running code inside the `with` block.

Upon exiting the `with` block, the lock is released.

> **_NOTE_**: when picking a lock name, please make sure the lock name is unique and has low collision probability. For example `acme-company-foo-system-parallel-batch-job` is a good name. `my-lock` is not.


## How it works
The core idea is that `lockable` provides a global server which keeps track of whether a lock has been acquired or not. All processes using `lockable` synchronize using the same server.

The server can be accesses via https, however, this Python library makes interacting with the server more pleasant.

`lockable` makes 3 endpoints available:
* `acquire` - accessed via `lockable.try_acquire(lock_name)`
* `heartbeat` - accessed via `lockable.try_heartbeat(lock_name)`
* `release` - accessed via `lockable.try_release(lock_name)`

`try_acquire(lock_name)` attempts to acquire the lock on the `lockable` server. If the lock is not available, this return `False`. If the lock is available, it is acquired and provided a finite lease (60 seconds by default). Once the lease expires, the lock is automatically released.

The main way to refresh the lease is by sending a heartbeat to the server, using `try_heartbeat(lock_name)`. If the lease is refreshed successfully, this returns `True`. If the lease refresh fails (e.g. because the lease has already expired), this returns `False`.

`try_release(lock_name)` immediately releases the lock, making it available for other processes.

This Python library automatically takes care of sending heartbeats to the `lockable` server by spwaning a separate thread and periodically hitting the `heartbeat` endpoint.


## Development

### Testing
```
make test
```

### Building and pushing changes
If you want to push to PiPy, credentials go in `.env.local`. See `.env.example` for a template.
```
# Just build
make build

#Build and upload latest version to TestPyPi
make test-publish
```
