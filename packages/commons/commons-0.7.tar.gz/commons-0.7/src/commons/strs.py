# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
String formatting, encoding, etc.
"""

__all__ = '''
and_join
cp1252_to_unicode
cp1252_to_unicode_translations
dos2unix
format
html2unicode
indent
nat_lang_join
or_join
remove_empty_lines
safe_ascii
underline
unicode2html
unicode_special
unwrap
'''.split()

import itertools, cgi, re, unittest

def format( *args ):
    """Formats the args as they would be by the C{print} built-in."""
    return ' '.join( itertools.imap( str, args ) )

def safe_ascii( s ):
    """Casts a Unicode string to a regular ASCCII string. This may be
    lossy."""
    if isinstance( s, unicode ) and s == str( s ):
        return str( s )
    else:
        return s

cp1252_to_unicode_translations = [ (u'\x80',u'\u20AC'),
                                   (u'\x82',u'\u201A'),
                                   (u'\x83',u'\u0192'),
                                   (u'\x84',u'\u201E'),
                                   (u'\x85',u'\u2026'),
                                   (u'\x86',u'\u2020'),
                                   (u'\x87',u'\u2021'),
                                   (u'\x88',u'\u02C6'),
                                   (u'\x89',u'\u2030'),
                                   (u'\x8A',u'\u0160'),
                                   (u'\x8B',u'\u2039'),
                                   (u'\x8C',u'\u0152'),
                                   (u'\x8E',u'\u017D'),
                                   (u'\x91',u'\u2018'),
                                   (u'\x92',u'\u2019'),
                                   (u'\x93',u'\u201C'),
                                   (u'\x94',u'\u201D'),
                                   (u'\x95',u'\u2022'),
                                   (u'\x96',u'\u2013'),
                                   (u'\x97',u'\u2014'),
                                   (u'\x98',u'\u02DC'),
                                   (u'\x99',u'\u2122'),
                                   (u'\x9A',u'\u0161'),
                                   (u'\x9B',u'\u203A'),
                                   (u'\x9C',u'\u0153'),
                                   (u'\x9E',u'\u017E'),
                                   (u'\x9F',u'\u0178') ]

def cp1252_to_unicode(x):
    """Converts characters 0x80 through 0x9f to their proper Unicode
    equivalents.  See
    U{http://www.intertwingly.net/stories/2004/04/14/i18n.html} for the nice
    translation table on which this is based."""
    for a,b in cp1252_to_unicode_translations:
        x = x.replace(a,b)
    return x

def unwrap(s):
    """
    Joins a bunch of lines.  L{s} is either a single string (which will be
    split on newlines into a list of strings) or a list of strings
    (representing lines).
    """
    if isinstance(s, str): s = s.strip().split('\n')
    return ' '.join( line.strip() for line in s )

def indent(s, ind = '  '):
    """
    Prefixes each line in L{s} with L{ind}.  L{s} can be either a string (which
    will be broken up into a list of lines) or a list of strings (treated as
    lines).  Returns a single (indented) string.
    """
    if isinstance(s, str): s = s.split('\n')
    return '\n'.join( ind + line for line in s )

def unindent(text, amt = None):
    """
    If L{amt} is 0, removes all leading whitespace from each line in L{text}.
    If L{amt} is L{None}, finds the smallest amount of leading whitespace on
    any non-empty line and removes that many chars from each line.  If L{amt}
    is positive, removes L{amt} chars from each line.
    """
    lines = text.split('\n')
    if amt == 0:
        return '\n'.join( line.lstrip() for line in lines )
    def count_indent(line):
        for i,c in enumerate(line):
            if not c.isspace(): return i
    if amt is None:
        amt = len(text) if text.strip() == '' else \
              min( count_indent(line) for line in lines if line.strip() != '' )
    return '\n'.join( line[amt:] for line in lines )

def remove_empty_lines(s):
    "Removes all empty lines (or lines of just whitespace)."
    return '\n'.join( line for line in s.split('\n') if line.strip() != '' )

def underline(s, sep):
    """
    Appends to L{s} a newline and a number of repetitions of L{sep}; the number
    of repetitions is the length of L{s}.
    """
    return s + '\n' + (sep * len(s))

def dos2unix(s):
    "Removes carriage returns."
    return s.replace('\r','')

def quotejs(s):
    "Escape a string as a JavaScript unicode string literal."
    return ''.join( r'\u%04x' % ord(c) for c in s )

unicode_special = re.compile(u'[\u0080-\uffff]')
def unicode2html(s):
    "Extends cgi.escape() with escapes for all unicode characters."
    # HTML special/Unicode char encoding is in base 10.
    return unicode_special.sub(lambda m: '&#%d;' % ord(m.group()),
                               cgi.escape(s))

def html2unicode(text):
    """
    Sort of a cgi.unescape (doesn't exist). Removes HTML or XML character
    references and entities from a text string.

    http://effbot.org/zone/re-sub.htm#unescape-html
    """
    import htmlentitydefs
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def nat_lang_join(xs, last_glue, two_glue = None, glue = ', '):
    """
    Natural-language join.  Join a sequence of strings together into a
    comma-separated list, but where the last pair is joined with the given
    special glue.  (You may also override the non-last glue, which defaults to
    a ', '.)

    @param xs: The sequence of strings.  This must be a list-like sequence, not
    a generated one.

    @param last_glue: The string used to join the final pair of elements, when
    there are more than two elements.

    @param two_glue: The string used to join both elements in a 2-element
    sequence.  Defaults to None, which means to use last_glue.

    @param glue: The string used to join all the other elements.
    """
    if len(xs) == 0: return ''
    elif len(xs) == 1: return xs[0]
    elif len(xs) == 2: return xs[0] + two_glue + xs[1]
    else: return glue.join(xs[:-1]) + last_glue + xs[-1]

def or_join(xs): return nat_lang_join(xs, ', or ', ' or ')
def and_join(xs): return nat_lang_join(xs, ', and ', ' and ')

class str_test( unittest.TestCase ):
    def test_nat_lang_join( self ):
        self.assertEqual( nat_lang_join( 'alpha beta gamma'.split(), ' | ' ),
                          'alpha, beta | gamma' )
        self.assertEqual( and_join( 'alpha beta gamma'.split() ),
                          'alpha, beta, and gamma' )
        self.assertEqual( or_join( 'alpha beta'.split() ),
                          'alpha or beta' )

if __name__ == '__main__':
    unittest.main()
