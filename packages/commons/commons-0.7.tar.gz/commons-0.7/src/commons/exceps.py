# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Exceptions and exception handling.

@var orig_excepthook: The original excepthook (as of the time this
module is first loaded). This just serves as a backup if it needs to
be restored.
"""

from decs import *
import sys

orig_excepthook = sys.excepthook

def handle_exceptions():
    """
    The default exception handler (prints a stack trace and the
    exception message), except it does not actually terminate the
    thread.
    """
    orig_excepthook( *sys.exc_info() )

class FailedInvariant( Exception ): pass

class InvariantChecker( GenericWrapper ):
    """
    Wrap an object and all of its methods with per-access
    invariants-checking.

    @todo: This code is incomplete and does not actually check
    invariants yet!
    """
    def __init__( self, obj, ignore=() ):
        def check_invariants():
            # TODO
            for invariant in self.invariants:
                if not invariant():
                    raise FailedInvariant()
        GenericWrapper.__init__(self, obj, None, check_invariants, ignore)
