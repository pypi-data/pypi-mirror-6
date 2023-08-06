#!/usr/bin/env bash

set -o errexit
cd "$( dirname "$0" )"
rm -r python-commons 2> /dev/null || true
svn export .. python-commons
cd python-commons
./setup.py register sdist bdist_egg upload
