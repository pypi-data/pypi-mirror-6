# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Threading.

@var stoppable_server_check_interval: The time interval (in seconds)
between checks by L{servers.StoppableServerMixin}s as to whether they
should stop.
"""

from decs import *
from log import *
import functools, threading

# time intervals between stoppable-server checks for stopping
stoppable_server_check_interval = 1

class Thread( threading.Thread ):
    """
    Adds extra features to the Thread class, including a way to
    request termination.
    """

    _lock = threading.Lock()
    _stopEvent = threading.Event()
    _doStop = False

    def __init__( self ):
        """
        Initializes the termination event.
        """
        threading.Thread.__init__( self )

    @classmethod
    def stop_all( cls ):
        """
        Requests the thread to terminate.
        """
        cls._lock.acquire()
        cls._doStop = True
        cls._lock.release()
        cls._stopEvent.set()

    @classmethod
    def wait_stop( cls, seconds = 0 ):
        """
        Wait for the specified number of seconds for an event.
        """
        Thread._stopEvent.wait( seconds )
        Thread._lock.acquire()
        ret = Thread._doStop
        Thread._lock.release()
        return ret

class StoppableThread( Thread ):
    def __init__( self, interval ):
        Thread.__init__( self )
        self.stop_event = threading.Event()
        self.interval = interval
    def run( self ):
        # TODO ideally, we'll wait on the shorter of the two wait-times,
        # but for now we know that wait_stop polls at least once per second
        while not ( self.stop_event.isSet() or
                Thread.wait_stop( self.interval ) ):
            self.loop()
    def stop( self ):
        self.stop_event.set()

#############################################################################

def spawn_thread( func, *args, **kwargs ):
    """
    Creates and starts a thread.
    """
    debug( 'commons.spawn_thread', 'spawning thread' )
    thread = threading.Thread( target = func, args = args, kwargs = kwargs )
    thread.start()
    return thread

#############################################################################

class SynchronizedObject( GenericWrapper ):
    """
    Wrap an object and all of its methods with synchronization.

    Example::
    
        class SynchronizedObject(GenericWrapper):
            ''' wrap an object and all of its methods with synchronization '''
            def _ _init_ _(self, obj, ignore=( ), lock=None):
                if lock is None:
                    import threading
                    lock = threading.RLock( )
                GenericWrapper._ _init_ _(self, obj, lock.acquire, lock.release, ignore)

    From the Python Cookbook.

    @copyright: O'Reilly Media
    """
    def __init__(self, obj, ignore=( ), lock=None):
        if lock is None:
            import threading
            lock = threading.RLock( )
        GenericWrapper.__init__(self, obj, lock.acquire, lock.release, ignore)

#############################################################################

def synchronized(func):
    '''
    Synchronized methods.

    From U{http://www.ddj.com/184406073}.

    @copyright: Phillip Eby
    
    Example::
    
        class SomeClass:
            """Example usage"""
            @synchronized
            def doSomething(self,someParam):
                """This method can only be entered 
                by one thread at a time"""
    '''
    @functools.wraps(func)
    def wrapper(self,*__args,**__kw):
        try:
            rlock = self._sync_lock
        except AttributeError:
            # setdefault is an atomic operation.
            # all c-implemented python operations are atomic due to the GIL.
            rlock = self.__dict__.setdefault( '_sync_lock',
                    threading.RLock() )
        rlock.acquire()
        try:
            return func(self,*__args,**__kw)
        finally:
            rlock.release()
    return wrapper

def synchronized_on(*rlocks):
    """
    This is useful for functions which aren't methods or when we want
    to synchronize on something other than C{self} (and note that we
    can synchronize on multiple locks).
    """
    def synchronized(func):
        @functools.wraps(func)
        def wrapper(self,*__args,**__kw):
            for rlock in rlocks:
                rlock.acquire()
            try:
                return func(self,*__args,**__kw)
            finally:
                for rlock in rlocks:
                    rlock.release()
        return wrapper
    return synchronized
