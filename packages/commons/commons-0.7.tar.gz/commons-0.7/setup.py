#!/usr/bin/env python
# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

import os,sys
sys.path.insert( 0, os.path.join( os.path.dirname( sys.argv[0] ), 'src' ) )
from commons import setup

pkg_info_text = """
Metadata-Version: 1.1
Name: commons
Version: 0.7
Author: Yang Zhang
Author-email: yaaang NOSPAM at REMOVECAPS gmail
Home-page: http://assorted.sourceforge.net/python-commons
Summary: Python Commons
License: Python Software Foundation License
Description: General-purpose library of utilities and extensions to the
        standard library.
Keywords: Python,common,commons,utility,utilities,library,libraries
Platform: any
Provides: commons
Classifier: Development Status :: 4 - Beta
Classifier: Environment :: No Input/Output (Daemon)
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: Python Software Foundation License
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
Classifier: Topic :: Communications
Classifier: Topic :: Database
Classifier: Topic :: Internet
Classifier: Topic :: Software Development :: Libraries :: Python Modules
Classifier: Topic :: System
Classifier: Topic :: System :: Filesystems
Classifier: Topic :: System :: Logging
Classifier: Topic :: System :: Networking
Classifier: Topic :: Text Processing
Classifier: Topic :: Utilities
"""

setup.run_setup( pkg_info_text,
                 #scripts = ['frontend/py_hotshot.py'],
                 )
