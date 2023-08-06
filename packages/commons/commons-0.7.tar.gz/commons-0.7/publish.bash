#!/usr/bin/env bash

post-stage() {
  epydoc -v -o $stagedir/doc src/commons/
}

echo 'Remember to keep versions in sync in all three locations:'
echo '__init__.py, README (Changes), setup.bash, and setup.py'

fullname='Python Commons'
version=0.7
license=psf
websrcs=( README )
rels=( pypi: )
. assorted.bash "$@"
