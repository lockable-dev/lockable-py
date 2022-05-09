#!/bin/bash
set -eux
PYTHON_VERSION="python3.8"
virtualenv -p "$(which $PYTHON_VERSION)" env
