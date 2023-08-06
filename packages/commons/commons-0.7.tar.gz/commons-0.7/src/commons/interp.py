# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
String interpolation. Example::

    language="Python"
    def printmsg():
        opinion = "favorite"
        print interp("My $opinion language is $language.")
"""

import re, string, sys, UserDict

class Chainmap(UserDict.DictMixin):
    """
    Combine multiple mappings for sequential lookup.

    From
    U{http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305268}.
    Modified to support object fields, e.g. C{"${a.b}"}.

    @copyright: Raymond Hettinger,
    """

    def __init__(self, *maps):
        self._maps = maps

    def __getitem__(self, key):
        keys = key.split('.')
        key = keys[ 0 ]
        attrs = keys[ 1 : ]
        value = None
        has_found = False
        for mapping in self._maps:
            try:
                value = mapping[ key ]
                has_found = True
                break
            except KeyError:
                pass
        if not has_found:
            raise KeyError(key)
        for attr in attrs:
            value = getattr( value, attr )
        return value

class LaxTemplate(string.Template):
    """
    From U{PythonPaste
    paste.script<http://svn.pythonpaste.org/Paste/Script/trunk/paste/script/copydir.py>}.
    This change of pattern allows for anything in braces, but only
    identifiers outside of braces.

    @copyright: Ian Bicking
    @license: MIT
    """

    pattern = r"""
    \$(?:
      (?P<escaped>\$)             |   # Escape sequence of two delimiters
      (?P<named>[_a-z][_a-z0-9]*) |   # delimiter and a Python identifier
      {(?P<braced>.*?)}           |   # delimiter and a braced identifier
      (?P<invalid>)                   # Other ill-formed delimiter exprs
    )
    """

def interp(s, dic = None):
    """
    This returns a unicode object when a substitution is made.

    From
    U{http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/335308}.

    @copyright: Michele Simionato

    @param s: The template string.
    @type s: str

    @param dic: Specifies bindings to use in addition to the calling
    frame's locals and globals. Defaults to C{None} for no additional
    bindings.
    @type dic: dict
    """
    caller = sys._getframe(1)
    if dic:
        m = Chainmap(dic, caller.f_locals, caller.f_globals)
    else:
        m = Chainmap(caller.f_locals, caller.f_globals)
    return LaxTemplate(s).substitute(m)
