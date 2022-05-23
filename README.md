# Lockable-dev
Official Python client for https://lockable.dev

Lockable is an easy-to-use, language-independent locking mechanism for multi-process workloads. Think of it as `flock`, but for distributed systems.


## Installation
```
pip install lockable-dev
```

## Usage
```
from lockable import Lock
with Lock('acme-company-my-lock'):
    #do stuff
```

## Advanced usage
```
from lockable import Lock
with Lock('acme-company-my-lock'):
    #do stuff
```

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
