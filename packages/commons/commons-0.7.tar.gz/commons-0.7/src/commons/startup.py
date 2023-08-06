# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Program startup functions and wrappers.
"""

from __future__ import absolute_import
from .log import ( critical, debug, config_logging )
from .environ import ( get_environs )
from .interp import interp
from os.path import basename
from sys import _current_frames
from threading import currentThread
import os, sys, unittest

class UnsetError( Exception ): pass

def get_arg_or_env( var, argv, error_name = None ):
    """
    Get a value based from C{argv[1]}; if that is unavailable, try
    looking at the corresponding environment variable C{var}.

    @todo: This is a weird, weird function. Do I really use it
    anywhere?
    """
    try:
        value = argv[ 1 ]
    except IndexError:
        try:
            value = os.environ[ var ]
        except KeyError:
            if error_name is not None:
                raise UnsetError, interp( '$error_name must be specified' )
            else:
                raise UnsetError
    return value

def config_psyco():
    """
    Try to enable Psyco profiling if the C{USE_PSYCO} environment
    variable is non-empty.
    """
    if 'USE_PSYCO' in os.environ:
        try:
            import psyco
        except ImportError:
            pass
        else:
            psyco.profile()

###########################################################

# TODO implement @deprecated
# @deprecated( get_usr_conf )
def get_config_path(
        file_env,
        file_default,
        dir_env = 'ASSORTED_CONF',
        dir_default = '.assorted' ):
    """
    Get the path to a configuration file. This tries the following:
        1. C{environ[file_env]}
        2. C{environ[dir_env]/file_default}
        3. C{$HOME/dir_default/file_default}
    """
    try:
        try:
            path = os.environ[ file_env ]
        except KeyError:
            try:
                path = paths.path( os.environ[ dir_env ] ) / \
                        file_default
            except KeyError:
                path = paths.path( os.environ[ 'HOME' ] ) / \
                        dir_default / \
                        file_default
        return path
    except:
        raise #return None

def get_usr_conf( *args, **kwargs ):
    """Gets a config file from $HOME."""
    return get_config_path( *args, **kwargs )

def get_sys_conf( env, default ):
    """Gets a config file from /etc/."""
    try:
        path = os.environ[ env ]
    except KeyError:
        path = paths.path( '/etc' ) / default
    return path

###########################################################

from signal import *

def dump_stack(*args):
    """
    Useful for debugging your program if it's spinning into infinite loops.
    Install this signal handler and issue your program a SIGQUIT to dump the
    main thread's stack, so you can see where it is.
    """
    from traceback import print_stack
    from cStringIO import StringIO
    s = StringIO()
    for tid, frame in _current_frames().iteritems():
        print >> s, 'thread', tid
        print_stack(f = frame, file = s)
    output = s.getvalue()
    print output
    sys.stdout.flush()
    print >> sys.stderr, output
    sys.stderr.flush()
    critical( '', output )

def command_name():
    return basename(sys.argv[0])

def run_main( main = None, do_force = False, runner = None,
              use_sigquit_handler = False, handle_exceptions = False ):
    """
    A feature-ful program starter. Configures logging and psyco, then
    runs the C{main} function defined in the caller's module, passing
    in C{sys.argv}.  If the C{PYDBG} environment variable is set, then
    runs C{main} in C{pdb}.  If the C{PYPROF} environment variable is
    set, then runs C{main} in C{cProfile}.  Finally, exits with
    C{main}'s return value.

    For example::

        def main(argv):
            print "Hello " + argv[1]
        run_main()
    """

    if use_sigquit_handler: signal( SIGQUIT, dump_stack )

    # TODO figure out a better solution for this
    config_logging()
    config_psyco()
    frame = sys._getframe( 1 if runner is None else 2 )

    try:
        name = frame.f_globals[ '__name__' ]
    except KeyError:
        pass
    else:
        if os.environ.get( 'PYTEST', '' ) != '':
            unittest.main()
        if do_force or runner is not None or name == '__main__':
            runner = ( ( lambda main, args: main( args ) )
                       if runner is None else runner )
            main = frame.f_globals[ 'main' ] if main is None else main
            do_debug = os.environ.get( 'PYDBG', '' ) != ''
            do_profile = os.environ.get( 'PYPROF', '' ) != ''

            try:
                if do_debug:
                    import pdb
                    signal(SIGINT, lambda *args: pdb.set_trace())
                    status = pdb.runcall( runner, main, sys.argv )
                elif do_profile:
                    from cProfile import runctx
                    container = []
                    try:
                        outpath = os.environ[ 'PYPROF' ] % \
                                  currentThread().getName()
                    except:
                        error( 'bad PYPROF:', os.environ[ 'PYPROF' ] )
                        status = runner( main, sys.argv )
                    else:
                        runctx( 'container[0] = runner( main, sys.argv )',
                                globals(), locals(), filename = outpath )
                        status = container[0]
                else:
                    status = runner( main, sys.argv )
            except ( KeyboardInterrupt, Exception ), ex:
                if handle_exceptions and not isinstance( ex, AssertionError ):
                    print >> sys.stderr, ex
                    sys.exit(1)
                else:
                    raise

            ## watchdog timer commits suicide if after 3 seconds we
            ## still have not exited
            #timer = threading.Timer( 3, suicide )
            #timer.start()
            debug( 'commons.run_main', 'terminating cleanly' )
            sys.exit( status )
