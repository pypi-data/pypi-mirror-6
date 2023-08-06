#!/usr/bin/env python
# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Common code for setup.py files.  Details about the Trove classifiers are
available at
U{http://pypi.python.org/pypi?%3Aaction=list_classifiers}.
"""

arg_keys = """
name
version
author
author_email
description: Summary
download_url: Download-url
long_description: Description
keywords: Keywords
url: Home-page
license
classifiers: Classifier
platforms: Platform
"""

import sys
if not hasattr(sys, "version_info") or sys.version_info < (2, 3):
    from distutils.core import setup
    _setup = setup
    def setup(**kwargs):
        for key in [
            # distutils >= Python 2.3 args
            # XXX probably download_url came in earlier than 2.3
            "classifiers", "download_url",
            # setuptools args
            "install_requires", "zip_safe", "test_suite",
            ]:
            if kwargs.has_key(key):
                del kwargs[key]
        # Only want packages keyword if this is a package,
        # only want py_modules keyword if this is a single-file module,
        # so get rid of packages or py_modules keyword as appropriate.
        if kwargs["packages"] is None:
            del kwargs["packages"]
        else:
            del kwargs["py_modules"]
        apply(_setup, (), kwargs)
else:
    from setuptools import setup, find_packages

def run_setup( pkg_info_text, srcdir = 'src', *orig_args, **orig_kwargs ):
    list_keys = set( [ 'Classifier' ] )
    pkg_info = {}
    for line in pkg_info_text.split( '\n' ):
        if line.strip() != '':
            if line.startswith( ' '*8 ):
                pkg_info[ key ] += line[ 7 : ]
            else:
                key, value = line.split( ': ', 1 )
                if key in list_keys:
                    try:
                        pkg_info[ key ].append( value )
                    except:
                        pkg_info[ key ] = [ value ]
                else:
                    pkg_info[ key ] = value

    args_nontranslations = set()
    args_translations = {}
    for line in arg_keys.split( '\n' ):
        if line.strip() != '':
            splitted = line.split( ': ', 1 )
            dest_name = splitted[ 0 ]
            if len( splitted ) == 2:
                source_name = splitted[ 1 ]
                args_translations[ source_name ] = dest_name
            else:
                args_nontranslations.add( dest_name )

    args = {}
    for key, value in pkg_info.iteritems():
        dest_name = None
        try:
            dest_name = args_translations[ key ]
        except KeyError:
            key = key.lower().replace('-','_')
            if key in args_nontranslations:
                dest_name = key
        if dest_name is not None:
            args[ dest_name ] = value

    # this also allows user to override our args
    args.update( orig_kwargs )
    args.update( {
        'package_dir': {'':srcdir},
        'packages': find_packages(srcdir),
        'zip_safe': True,
    } )

    setup( *orig_args, **args )
