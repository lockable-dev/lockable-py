# Lockable-dev
Official Python client for https://lockable.dev

## Usage
```
import lockable
```


## Building and pushing changes
If you want to push to PiPy, credentials go in `.env.local`. See `.env.example` for a template.
```
# Just build
make build

#Build and upload latest version to TestPyPi
make test-publish
```
