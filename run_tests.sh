#!/bin/bash

# Run application's unit tests

set -o nounset
set -o errexit
set +o xtrace

python3 -m unittest --catch --failfast --verbose
