# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Sequences, streams, and generators.

@var default_chunk_size: The default chunk size used by L{chunkify}.
"""

from __future__ import ( absolute_import, with_statement )

from cStringIO import StringIO
from cPickle import *
from struct import pack, unpack
from contextlib import closing
from itertools import ( chain, count, ifilterfalse, islice,
                        izip, repeat, tee, takewhile )
from commons.log import warning

__all__ = '''
default_chunk_size
read_pickle
read_pickles
safe_pickler
write_pickle
streamlen
chunkify
total
ClosedError
PersistentConsumedSeq
PersistentSeq
pairwise
argmax
argmin
concat
flatten
grouper
chunker
countstep
take
delimit
interleave
group_as_subseqs
span
'''.split()

default_chunk_size = 8192

def read_pickle( read, init = '', length_thresh = 100000 ):
    """
    Given a reader function L{read}, reads in pickled objects from it. I am a
    generator which yields unpickled objects. I assume that the pickling
    is "safe," done using L{safe_pickler}.

    @param read: The reader function that reads from a stream. It should take
    a single argument, the number of bytes to consume.
    @type read: function

    @return: A tuple whose first element is the deserialized object or None if
    EOF was encountered, and whose second element is the remainder bytes until
    the EOF that were not consumed by unpickling.
    @rtype: (object, str)
    """
    with closing( StringIO() ) as sio:
        obj = None # return this if we hit eof (not enough bytes read)
        sio.write( init )

        def read_until( target ):
            remain = target - streamlen( sio )
            if remain > 0:
                chunk = read( remain )
                # append to end
                sio.seek(0,2)
                sio.write( chunk )
            offset = streamlen( sio )
            sio.seek(0)
            return offset >= target

        if read_until(4):
            lengthstr = sio.read(4)
            (length,) = unpack('i4', lengthstr)
            if length_thresh is not None and length > length_thresh or \
                    length <= 0:
                warning( 'read_pickle',
                         'got length', length,
                         'streamlen', streamlen(sio),
                         'first bytes %x %x %x %x' % tuple(map(ord,lengthstr)) )
            if read_until(length+4):
                # start reading from right after header
                sio.seek(4)
                obj = load(sio)

        return ( obj, sio.read() )

def read_pickles( read ):
    """
    Reads all the consecutively pickled objects from the L{read} function.
    """
    while True:
        pair = ( obj, rem ) = read_pickle( read )
        if obj is None: break
        yield pair

class safe_pickler( object ):
    def __init__( self, protocol = HIGHEST_PROTOCOL ):
        self.sio = StringIO()
        self.pickler = Pickler( self.sio, protocol )
    def dumps( self, obj ):
        """
        Pickle L{obj} but prepends the serialized length in bytes.
        """
        self.pickler.clear_memo()
        self.sio.seek(0)
        self.pickler.dump(obj)
        self.sio.truncate()
        msg = self.sio.getvalue()
        return pack('i4', self.sio.tell()) + msg

def write_pickle( obj, write ):
    """
    Write L{obj} using function L{write}, in a safe, pickle-able fashion.
    """
    return write( safe_pickle( obj ) )

def streamlen( stream ):
    """
    Get the length of a stream (e.g. file stream or StringIO).
    Tries to restore the original position in the stream.
    """
    orig_pos = stream.tell()
    stream.seek(0,2) # seek to 0 relative to eof
    length = stream.tell() # get the position
    stream.seek(orig_pos) # return to orig_pos
    return length

def chunkify( stream, chunk_size = default_chunk_size ):
    """
    Given an input stream (an object exposing a file-like interface),
    reads data in from it one chunk at a time. This is a generator
    which yields those chunks as they come.

    @param stream: The input stream.
    @type stream: stream

    @param chunk_size: The size of the chunk (usually the number of
    bytes to read).
    @type chunk_size: int
    """
    offset = 0
    while True:
        chunk = stream.read( chunk_size )
        if not chunk:
            break
        yield offset, chunk
        offset += len( chunk )

def total( iterable ):
    """
    Counts the number of items in an iterable. Note that this will
    consume the elements of the iterable, and if the iterable is
    infinite, this will not halt.

    @param iterable: The iterable to count.
    @type iterable

    @return: The number of elements consumed.
    @rtype: int
    """
    return sum( 1 for i in iterable )

#class FilePersistence():
#    def __init__( self ):
#        
#
#class DbPersistence():
#    def __init__( self ):
#        

class ClosedError( Exception ): pass

class PersistentConsumedSeq( object ):
    """
    I generate C{[0, 1, ...]}, like L{count}, but I can also
    save my state to disk. Similar to L{PersistentSeq}, but instead of
    committing on each call to L{next}, require manual explicit calls
    to L{commit}. I'm useful for generating unique IDs.

    Why not simply use L{PersistentSeq} instead of me? You usually
    can. However, some applications use me for efficiency. For
    instance, consider an application that generates a lot of network
    packets (with sequence numbers), but only sends a small fraction
    of them out onto the network. If we only want to guarantee the
    uniqueness of sequence numbers that are exposed to the world, we
    need only commit when upon sending a packet, and not on generating
    a packet (L{next}). This could avoid excessive writes.

    @ivar seqno: The next sequence number to be generated.
    @type seqno: int
    """
    def __init__( self, path ):
        """
        @param path: File to save my state in. I keep this file open.
        @type path: str
        """
        try:
            self.log = file( path, 'r+' )
        except IOError, ex:
            if ex.errno == 2:
                self.log = file( path, 'w+' )
            else:
                raise
        contents = self.log.read()
        if len( contents ) > 0:
            self.seqno = int( contents )
        else:
            self.seqno = 0
        self.max_commit = self.seqno
    def next( self ):
        """
        @return: The next number in the sequence.
        @rtype: int

        @raise ClosedError: If I was previously L{close}d.
        """
        if self.log is None:
            raise ClosedError()
        self.seqno += 1
        return self.seqno - 1
    def commit( self, seqno ):
        """
        @param seqno: If this is the maximum committed sequence
        number, then commit this sequence number (to disk). The
        semantics will get weird if you pass in sequence numbers that
        haven't been generated yet.
        
        @type seqno: int

        @return: The maximum sequence number ever committed (possibly
        L{seqno}).
        @rtype: int

        @raise ClosedError: If I was previously L{close}d.
        """
        if self.log is None:
            raise ClosedError()
        if seqno > self.max_commit:
            # TODO use a more flexible logging system that can switch
            # between Python's logging module and Twisted's log module
            self.max_commit = seqno
            self.log.seek( 0 )
            # yes I write +1 here
            self.log.write( str( seqno + 1 ) )
            self.log.truncate()
            self.log.flush()
        return self.max_commit
    def close( self ):
        """
        Closes the log file. No more operations can be performed.
        """
        self.log.close()
        self.log = None

class PersistentSeq( PersistentConsumedSeq ):
    """
    I generate C{[0, 1, ...]}, like L{count}, but I can also
    save my state to disk. I save my state immediately to disk on each
    call to L{next}.
    """
    def __init__( self, path ):
        """
        @param path: File to save my state in. I keep this file open.
        @type path: str
        """
        PersistentConsumedSeq.__init__( self, path )
    def next( self ):
        """
        Generates the next number in the sequence and immediately
        commits it.
        """
        cur = PersistentConsumedSeq.next( self )
        self.commit( cur )
        return cur

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    try:
        b.next()
    except StopIteration:
        pass
    return izip(a, b)

def argmax(sequence, fn=None):
    """Two usage patterns:
    C{argmax([s0, s1, ...], fn)}
    C{argmax([(fn(s0), s0), (fn(s1), s1), ...])}
    Both return the si with greatest fn(si)"""
    if fn is None:
        return max(sequence)[1]
    else:
        return max((fn(e), e) for e in sequence)[1]

def argmin(sequence, fn=None):
    """Two usage patterns:
    C{argmin([s0, s1, ...], fn)}
    C{argmin([(fn(s0), s0), (fn(s1), s1), ...])}
    Both return the si with smallest fn(si)"""
    if fn is None:
        return min(sequence)[1]
    else:
        return min((fn(e), e) for e in sequence)[1]

def concat(listOfLists):
    return list(chain(*listOfLists))

def flatten( stream ):
    """
    For each item yielded by L{stream}, if that item is itself an
    iterator/generator, then I will recurse into C{flatten(gen)};
    otherwise, I'll yield the yielded item. Thus, I essentially
    "flatten" out a tree of iterators.

    I test whether something is an iterator/generator simply by
    checking to see if it has a C{next} attribute. Note that this
    won't include any iterable, so things like L{list}s are yielded
    like any regular item. This is my author's desired behavior!

    I am useful for coroutines, a la DeferredGenerators from Twisted.

    See also:
    U{http://mail.python.org/pipermail/python-list/2003-October/232874.html}
    """
    for item in stream:
        if hasattr( item, 'next' ):
            for item in flatten( item ):
                yield item
        else:
            yield item

def grouper(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return izip(*[chain(iterable, repeat(padvalue, n-1))]*n)

def chunker( n, iterable, in_place = False ):
    """
    Like L{grouper} but designed to scale for larger L{n}.  Also, does
    not perform padding.  The end of the stream is reached when we
    yield a chunk with fewer than L{n} items.
    """
    i = -1
    chunk = [ None ] * n
    for i, item in enumerate( iterable ):
        chunk[ i % n ] = item
        if ( i + 1 ) % n == 0:
            yield chunk
            if not in_place: chunk = [ None ] * n
    else:
        if i % n < n - 1:
            del chunk[ ( i + 1 ) % n : ]
            yield chunk

def countstep(start, step):
    """
    Generate [start, start+step, start+2*step, start+3*step, ...].
    """
    i = start
    while True:
        yield i
        i += step

def take(n, seq):
    return list(islice(seq, n))

def delimit(sep, xs):
    for x in xs:
        yield x
        break
    for x in xs:
        yield sep
        yield x

# TODO not quite right
def interleave(xs, ys):
    return concat(izip( xs, ys ))

def span(pred, xs):
    """
    Returns (successes, failures), where successes is the sequence of any
    consecutive elements at the head of L{xs} that satisfy the predicate, and
    second is everything else.
    """
    xs = iter(xs)
    first_failure = []
    def successes():
        for x in xs:
            if not pred(x):
                first_failure.append(x)
                break
            yield x
    return list(successes()), chain(first_failure, xs)

def group_as_subseqs(xs, key = lambda x: x):
    """
    Takes a sequence and breaks it up into multiple subsequences, which are
    groups keyed on L{key}.

    >>> map(list, group_as_subseqs(range(10), lambda x: x/3))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    """
    xs = iter(xs)
    while True:
        setfirst = False
        for x in xs:
            first = x
            setfirst = True
            break
        if not setfirst: break # We've hit the end
        firstkey = key(first)
        successes, xs = span(lambda x: key(x) == firstkey, xs)
        yield chain([first], successes)

import unittest

class test_seqs(unittest.TestCase):
    def test_span(self):
        xs,ys = span(lambda x: x < 5, range(10))
        self.assertEqual(list(xs), range(5))
        self.assertEqual(list(ys), range(5,10))
    def test_group(self):
        a,b,c,d = group_as_subseqs(range(10), lambda x: x / 3)
        self.assertEqual(list(a), range(0,3))
        self.assertEqual(list(b), range(3,6))
        self.assertEqual(list(c), range(6,9))
        self.assertEqual(list(d), range(9,10))

if __name__ == '__main__':
    unittest.main()
