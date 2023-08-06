#!/usr/bin/env python
# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Standalone program for tracing a Python program. Simply specify the module whose C{main} function we want to run.

@todo: Document this more completely.
"""

from __future__ import absolute_import
from .startup import run_main
import imp, linecache, sys

class Tracer( object ):
    def __init__( self ):
        self.do_trace = False

    def trace( self, frame, event, arg ):
        c = frame.f_code
        g = frame.f_globals
        # events: line, call
        module_name = g["__name__"]
        function_name = c.co_name
        if event == 'line' and ( self.do_trace and function_name.startswith( 'forms' ) or function_name.startswith( 'select_form' ) ):
            self.do_trace = True
            lineno = frame.f_lineno
            filename = '<unknown file>'
            line = '<line unavailable>'
            try:
                filename = g["__file__"]
                if (filename.endswith(".pyc") or
                    filename.endswith(".pyo")):
                    filename = filename[:-1]
                line = linecache.getline( filename, lineno )
                if line is None or line.strip() == '':
                    line = '<line unavailable>'
            except KeyError:
                pass
            print '%s:%d:\t%s:%s(%s):\t%s' % ( filename,
                    lineno,
                    module_name,
                    function_name,
                    ', '.join( c.co_varnames[ : c.co_argcount ] ),
                    line.rstrip() )
        return self.trace

def main( argv ):
    module_name = argv[ 1 ]
    args = argv[ 1 : ]

    module = imp.load_module( module_name,
                              *imp.find_module( module_name ) )

    tracer = Tracer()
    sys.settrace( tracer.trace )

    module.main( args )

run_main()
