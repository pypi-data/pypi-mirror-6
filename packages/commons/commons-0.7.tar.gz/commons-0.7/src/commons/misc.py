# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Miscellanea.
"""

__all__ = '''
TerminalController
cleartimeout
days
default_if_none
generate_bit_fields
remove_colors
run
sendmail
seq
settimeout
timeout_exception
wall_clock
'''.split()

#
# Email
#

import smtplib

def sendmail(sender, to, subj, body):
    msg = "From: %s\r\nTo: %s\r\nSubject:%s\r\n\r\n%s" % (sender, to, subj, body)
    server = smtplib.SMTP('localhost')
    try:
        server.set_debuglevel(False)
        server.sendmail(sender, to, msg)
    finally:
        server.quit()

#
# Date/Time
#

from datetime import timedelta

def days(td):
    """Returns the ceil(days in the timedelta L{td})."""
    return td.days + (1 if td - timedelta(days = td.days) > timedelta() else 0)

#
# Bit fields
#

def generate_bit_fields(count):
    """
    A generator of [2^i] for i from 0 to (count - 1). Useful for,
    e.g., enumerating bitmask flags::

        red, yellow, green, blue = generate_bit_fields(4)
        color1 = blue
        color2 = red | yellow

    @param count: The number of times to perform the left-shift.
    @type count: int
    """
    j = 1
    for i in xrange( count ):
        yield j
        j <<= 1

#
# Timing
#

from time import *
from contextlib import *
from signal import *

@contextmanager
def wall_clock(output):
    """
    A simple timer for code sections.

    Example::

      t = [0]
      with wall_clock(t):
        sleep(1)
      print "the sleep operation took %d seconds" % t[0]

    @param output: The resulting time is put into index 0 of C{output}.
    @type output: index-writeable
    """
    start = time()
    try:
        yield
    finally:
        end = time()
        output[0] = end - start

class timeout_exception(Exception): pass

def settimeout(secs):
    """
    Set the signal handler for SIGALRM to raise timeout_exception, and call
    alarm(secs).
    """
    def handle(sig, frame): raise timeout_exception()
    signal(SIGALRM, handle)
    alarm(secs)

def cleartimeout(): alarm(0)

#
# Functional
#

def default_if_none(x, d):
    """
    Returns L{x} if it's not None, otherwise returns L{d}.
    """
    if x is None: return d
    else: return x

def seq(f, g):
    """
    Evaluate 0-ary functions L{f} then L{g}, returning L{g()}.
    """
    f()
    return g()

#
# Processes
#

from subprocess import CalledProcessError, PIPE, Popen

def run(cmd):
  """
  Run the given command (a list of program and argument strings) and return the
  stdout as a string, raising a L{CalledProcessError} if the program exited
  with a non-zero status.  Different from check_call because I return the
  (piped) stdout.
  """
  p = Popen(cmd, stdout=PIPE)
  stdout = p.communicate()[0]
  if p.returncode != 0: raise CalledProcessError(p.returncode, cmd)
  return stdout

#
# Terminal ANSI coloring
#

import sys, re

class TerminalController:
    """
    From U{http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/475116}.

    A class that can be used to portably generate formatted output to
    a terminal.  
    
    `TerminalController` defines a set of instance variables whose
    values are initialized to the control sequence necessary to
    perform a given action.  These can be simply included in normal
    output to the terminal:

        >>> term = TerminalController()
        >>> print 'This is '+term.GREEN+'green'+term.NORMAL

    Alternatively, the `render()` method can used, which replaces
    '${action}' with the string required to perform 'action':

        >>> term = TerminalController()
        >>> print term.render('This is ${GREEN}green${NORMAL}')

    If the terminal doesn't support a given action, then the value of
    the corresponding instance variable will be set to ''.  As a
    result, the above code will still work on terminals that do not
    support color, except that their output will not be colored.
    Also, this means that you can test whether the terminal supports a
    given action by simply testing the truth value of the
    corresponding instance variable:

        >>> term = TerminalController()
        >>> if term.CLEAR_SCREEN:
        ...     print 'This terminal supports clearning the screen.'

    Finally, if the width and height of the terminal are known, then
    they will be stored in the `COLS` and `LINES` attributes.
    """
    # Cursor movement:
    BOL = ''             #: Move the cursor to the beginning of the line
    UP = ''              #: Move the cursor up one line
    DOWN = ''            #: Move the cursor down one line
    LEFT = ''            #: Move the cursor left one char
    RIGHT = ''           #: Move the cursor right one char

    # Deletion:
    CLEAR_SCREEN = ''    #: Clear the screen and move to home position
    CLEAR_EOL = ''       #: Clear to the end of the line.
    CLEAR_BOL = ''       #: Clear to the beginning of the line.
    CLEAR_EOS = ''       #: Clear to the end of the screen

    # Output modes:
    BOLD = ''            #: Turn on bold mode
    BLINK = ''           #: Turn on blink mode
    DIM = ''             #: Turn on half-bright mode
    REVERSE = ''         #: Turn on reverse-video mode
    NORMAL = ''          #: Turn off all modes

    # Cursor display:
    HIDE_CURSOR = ''     #: Make the cursor invisible
    SHOW_CURSOR = ''     #: Make the cursor visible

    # Terminal size:
    COLS = None          #: Width of the terminal (None for unknown)
    LINES = None         #: Height of the terminal (None for unknown)

    # Foreground colors:
    BLACK = BLUE = GREEN = CYAN = RED = MAGENTA = YELLOW = WHITE = ''
    
    # Background colors:
    BG_BLACK = BG_BLUE = BG_GREEN = BG_CYAN = ''
    BG_RED = BG_MAGENTA = BG_YELLOW = BG_WHITE = ''
    
    _STRING_CAPABILITIES = """
    BOL=cr UP=cuu1 DOWN=cud1 LEFT=cub1 RIGHT=cuf1
    CLEAR_SCREEN=clear CLEAR_EOL=el CLEAR_BOL=el1 CLEAR_EOS=ed BOLD=bold
    BLINK=blink DIM=dim REVERSE=rev UNDERLINE=smul NORMAL=sgr0
    HIDE_CURSOR=cinvis SHOW_CURSOR=cnorm""".split()
    _COLORS = """BLACK BLUE GREEN CYAN RED MAGENTA YELLOW WHITE""".split()
    _ANSICOLORS = "BLACK RED GREEN YELLOW BLUE MAGENTA CYAN WHITE".split()

    def __init__(self, term_stream=sys.stdout, force=False):
        """
        Create a `TerminalController` and initialize its attributes
        with appropriate values for the current terminal.
        `term_stream` is the stream that will be used for terminal
        output; if this stream is not a tty, then the terminal is
        assumed to be a dumb terminal (i.e., have no capabilities).
        """
        # Curses isn't available on all platforms
        try: import curses
        except: return

        # If the stream isn't a tty, then assume it has no capabilities.
        if not force and not term_stream.isatty(): return

        # Check the terminal type.  If we fail, then assume that the
        # terminal has no capabilities.
        try: curses.setupterm()
        except: return

        # Look up numeric capabilities.
        self.COLS = curses.tigetnum('cols')
        self.LINES = curses.tigetnum('lines')
        
        # Look up string capabilities.
        for capability in self._STRING_CAPABILITIES:
            (attrib, cap_name) = capability.split('=')
            setattr(self, attrib, self._tigetstr(cap_name) or '')

        # Colors
        set_fg = self._tigetstr('setf')
        if set_fg:
            for i,color in zip(range(len(self._COLORS)), self._COLORS):
                setattr(self, color, curses.tparm(set_fg, i) or '')
        set_fg_ansi = self._tigetstr('setaf')
        if set_fg_ansi:
            for i,color in zip(range(len(self._ANSICOLORS)), self._ANSICOLORS):
                setattr(self, color, curses.tparm(set_fg_ansi, i) or '')
        set_bg = self._tigetstr('setb')
        if set_bg:
            for i,color in zip(range(len(self._COLORS)), self._COLORS):
                setattr(self, 'BG_'+color, curses.tparm(set_bg, i) or '')
        set_bg_ansi = self._tigetstr('setab')
        if set_bg_ansi:
            for i,color in zip(range(len(self._ANSICOLORS)), self._ANSICOLORS):
                setattr(self, 'BG_'+color, curses.tparm(set_bg_ansi, i) or '')

    def _tigetstr(self, cap_name):
        # String capabilities can include "delays" of the form "$<2>".
        # For any modern terminal, we should be able to just ignore
        # these, so strip them out.
        import curses
        cap = curses.tigetstr(cap_name) or ''
        return re.sub(r'\$<\d+>[/*]?', '', cap)

    def render(self, template):
        """
        Replace each $-substitutions in the given template string with
        the corresponding terminal control string (if it's defined) or
        '' (if it's not).
        """
        return re.sub(r'\$\$|\${\w+}', self._render_sub, template)

    def _render_sub(self, match):
        s = match.group()
        if s == '$$': return s
        else: return getattr(self, s[2:-1])

    def wrap(self, s, color):
        """
        Wraps L{s} in L{color} (resets color to NORMAL at the end).
        """
        return self.render( '${%s}%s${NORMAL}' % (color, s) )

remove_colors_pat = re.compile('\033\\[[0-9;]*m')
def remove_colors(s):
    'Removes ANSI escape codes (e.g. those for terminal colors).'
    return remove_colors_pat.sub('', s)

import unittest

class color_test( unittest.TestCase ):
    def test_round_trip( self ):
        tc = TerminalController()
        template = '${GREEN}green${BLUE}blue${NORMAL}normal'
        rendered = tc.render( template )
        removed  = remove_colors( rendered )
        self.assertEqual( removed, 'greenbluenormal' )

if __name__ == '__main__':
    unittest.main()
