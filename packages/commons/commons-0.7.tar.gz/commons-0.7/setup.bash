#!/usr/bin/env bash

cd "$( dirname "$0" )"
. common.bash

pkg=python-commons
. simple-setup.bash

version=$( python -c "import sys; print '.'.join(map(str,sys.version_info[:2]))" )
install lib/python$version/site-packages/ src/commons
