# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""Processes, idling, and signals."""

from logging import *
import os, signal, time

def suicide():
    """Force-kill the current process."""
    os.kill( os.getpid(), signal.SIGKILL )

#############################################################################

class Sleeper( object ):
    """Sleeper class. Goes to sleep forever."""
    @classmethod
    def sleep( cls ):
        """
        Calls C{time.sleep} for 100000 seconds at a time in a
        while-true loop.
        """
        while True:
            time.sleep( 100000 )

#############################################################################

class SigTerm( Exception ): pass

def handle_signal( signum, frame ):
    """
    Generic signal handler that logs the received signal to the
    "signal" logging channel (log level INFO) and then raises
    L{SigTerm} if it was not previously raised.

    @param signum: The signal's numeric value (see C{man 7 signal}).

    @param frame: Ignored.

    @raise SigTerm: Only once.
    """
    global got_signal
    info( 'signal', 'got signal', str( signum ) )
    if not got_signal:
        got_signal = True
        raise SigTerm

def handle_signals( *sigs ):
    """
    For each given signal, register the L{handle_signal} as its
    handler.

    @param sigs: The set of sigs to iterate over.
    @type sigs: set
    """
    global got_signal
    got_signal = False
    for sig in sigs:
        signal.signal( signal.SIGTERM, handle_signal )
