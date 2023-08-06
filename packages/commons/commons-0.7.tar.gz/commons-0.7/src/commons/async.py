# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Asynchronous utilities for use with the
U{Twisted<http://twistedmatrix.com/>} library.
"""

from twisted.internet import defer, reactor

def async_sleep( seconds ):
    """
    Acts as the asynchronous version of C{time.sleep}.

    @param seconds: The amount of time in seconds to sleep.
    @type seconds: float

    @return: The C{defer.Deferred} that will be fired on wake-up.
    @rtype: defer.Deferred
    """
    d = defer.Deferred()
    reactor.callLater( seconds, lambda: d.callback( None ) )
    return d

def asynchronized( func ):
    """
    Acts as the asynchronous version of a C{synchronized} decorator
    (inspired by Java's keyword). Ensures that no event-handling path
    (the asynchronous equivalent to threads) will enter the function
    if another one is currently in it (which can happen if the current
    "thread" is itself waiting on a deferred, thus giving the reactor
    an opportunity to execute the competing "thread").

    Provides additional protection against U{Twisted bug
    411<http://twistedmatrix.com/trac/ticket/411>}. In this case, if
    too many acquisition requests are chained onto the deferred which
    is fired on release, then the stack will overflow. This is
    circumvented by maintaining a queue of closures and deferreds
    which is checked on each release, to keep the callback chain
    "flat."

    @param func: The function to decorate.
    @type func: function

    @return: The "thread-safe" version of the function.
    @rtype: function
    """
    def wrapper( self, *args, **kwargs ):
        try:
            q = self._sync_queue
        except AttributeError:
            q = self._sync_queue = []
        def release( result ):
            invoke, d = q[0]
            # actually perform the callback on the outer
            # deferred; the deferred running this cb() should
            # just terminate and be discarded
            d.callback( result )
            
            del q[0]
            if len( q ) > 0:
                invoke, d = q[0]
                # we're tempted to do just run invoke() directly, but
                # that would lead to the same stack explosion
                reactor.callLater( 0, invoke )
            return result
        def invoke():
            return defer.maybeDeferred( func, self, *args, **kwargs ).addCallback( release )
        d = defer.Deferred()
        q.append( ( invoke, d ) )
        if len( q ) == 1:
            reactor.callLater( 0, invoke )
        return d
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper
