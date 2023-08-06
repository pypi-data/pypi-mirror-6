# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Decorators and decorator utilities.

@todo: Move the actual decorators to modules based on their topic.
"""

from __future__ import with_statement
import functools, inspect, xmlrpclib
from cPickle import *

def recursion_guard(retval, guard_name = "____recursion_guard"):
    """
    Prevents a methods from recursively calling itself. On recursion, it will
    return retval instead. Note that this only protects methods, not functions.
    To implement something similar for functions may call for some thread-local
    state or some stack-walking.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kw):
            if getattr(self, guard_name, False):
                return retval
            setattr(self, guard_name, True)
            try:
                return func(self, *args, **kw)
            finally:
                setattr(self, guard_name, False)
        return wrapper
    return decorator

def wrap_callable(any_callable, before, after):
    """
    Wrap any callable with before/after calls.

    From the Python Cookbook. Modified to support C{None} for
    C{before} or C{after}.

    @copyright: O'Reilly Media

    @param any_callable: The function to decorate.
    @type any_callable: function
    
    @param before: The pre-processing procedure. If this is C{None}, then no pre-processing will be done.
    @type before: function
    
    @param after: The post-processing procedure. If this is C{None}, then no post-processing will be done.
    @type after: function
    """
    def _wrapped(*a, **kw):
        if before is not None:
            before( )
        try:
            return any_callable(*a, **kw)
        finally:
            if after is not None:
                after( )
    # In 2.4, only: _wrapped.__name__ = any_callable.__name__
    return _wrapped

class GenericWrapper( object ):
    """
    Wrap all of an object's methods with before/after calls. This is
    like a decorator for objects.

    From the I{Python Cookbook}.

    @copyright: O'Reilly Media
    """
    def __init__(self, obj, before, after, ignore=( )):
        # we must set into __dict__ directly to bypass __setattr__; so,
        # we need to reproduce the name-mangling for double-underscores
        clasname = 'GenericWrapper'
        self.__dict__['_%s__methods' % clasname] = {  }
        self.__dict__['_%s__obj' % clasname] = obj
        for name, method in inspect.getmembers(obj, inspect.ismethod):
            if name not in ignore and method not in ignore:
                self.__methods[name] = wrap_callable(method, before, after)
    def __getattr__(self, name):
        try:
            return self.__methods[name]
        except KeyError:
            return getattr(self.__obj, name)
    def __setattr__(self, name, value):
        setattr(self.__obj, name, value)

##########################################################

def xmlrpc_safe(func):
    """
    Makes a procedure "XMLRPC-safe" by returning 0 whenever the inner
    function returns C{None}. This is useful because XMLRPC requires
    return values, and 0 is commonly used when functions don't intend
    to return anything.

    Also, if the procedure returns a boolean, it will be wrapped in
    C{xmlrpclib.Boolean}.

    @param func: The procedure to decorate.
    @type func: function
    """
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        result = func(*args,**kwargs)
        if result is not None:
            if type( result ) == bool:
                return xmlrpclib.Boolean( result )
            else:
                return result
        else:
            return 0
    return wrapper

##########################################################

def file_memoized(serializer, deserializer, pathfunc):
    """
    The string result of the given function is saved to the given path.

    Example::

        @file_memoized(lambda x,f: f.write(x),
                       lambda f: f.read(),
                       lambda: "/tmp/cache")
        def foo(): return "hello"

        @file_memoized(pickle.dump,
                       pickle.load,
                       lambda x,y: "/tmp/cache-%d-%d" % (x,y))
        def foo(x,y): return "hello %d %d" % (x,y)

    @param serializer: The function to serialize the return value into a
                       string.  This should take the return value object and
                       the file object.
    @type serializer: function

    @param deserializer: The function te deserialize the cache file contents
                         into the return value.  This should take the file
                         object and return a string.
    @type deserializer: function

    @param pathfunc: Returns the path where the files should be saved.  This
                     should be able to take the same arguments as the original
                     function.
    @type pathfunc: str
    """
    def dec(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            p = pathfunc(*args, **kwargs)
            try:
                with file(p) as f:
                    return deserializer(f)
            except IOError, (errno, errstr):
                if errno != 2: raise
                with file(p, 'w') as f:
                    x = func(*args, **kwargs)
                    serializer(x, f)
                    return x
        return wrapper
    return dec

def file_string_memoized(pathfunc):
    """
    Wrapper around L{file_memoized} that expects the decorated function to
    return strings, so the string is written verbatim.
    """
    return file_memoized(lambda x,f: f.write(x), lambda f: f.read(), pathfunc)

def pickle_memoized(pathfunc):
    """
    Wrapper around L{file_memoized} that uses pickle.
    """
    bindump = lambda x,f: dump(x,f,2)
    binload = lambda x,f: load(x,f,2)
    return file_memoized(bindump, binload, pathfunc)
