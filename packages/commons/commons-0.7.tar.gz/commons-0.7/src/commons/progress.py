# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
Long-running processes and facilities to let them report their progress.
"""

from commons.log import *
from commons.seqs import *
import urllib2, sys

def urlopen_progress( url, output_stream = None, fields = 'OoRrtcl', chunk_size = 4096 ):
    """
    Progress reporter for urlopen(). This is a generator which, upon
    receipt of each chunk of data, yields a tuple of values. This
    tuple reports data about the progress of the download; the exact
    values yielded can be configured.

    Based on
    U{http://mail.python.org/pipermail/python-list/2006-January/320635.html}.

    @param url: The URL to fetch.
    @type url: str

    @param output_stream: The file-like stream object to write to.
    @type output_stream: stream

    @param fields: A set of characters indicating what data to
    report. The following characters have meaning:
        - O: offset where the first byte of the latest chunk is to be
          written
        - o: offset percentage
        - R: received number of bytes (offset + length of latest
          chunk)
        - r: received percentage
        - t: total number of bytes
        - c: the latest chunk
        - l: the length of the latest chunk
    @type fields: str

    @param chunk_size: The requested chunk size.
    @type chunk_size: int
    """
    chunk_size = 4096
    result = urllib2.urlopen( url )
    headers = result.info()
    total = int( headers[ 'Content-Length' ] )
    for offset, chunk in chunkify( result, chunk_size ):
        if output_stream is not None:
            output_stream.write( chunk )
        values = []
        offset_ratio = float(offset)/float(total)
        received = offset + len( chunk )
        received_ratio = float(received)/float(total)
        if 'O' in fields:
            values.append( offset )
        if 'o' in fields:
            values.append( offset_ratio )
        if 'R' in fields:
            values.append( received )
        if 'r' in fields:
            values.append( received_ratio )
        if 't' in fields:
            values.append( total )
        if 'c' in fields:
            values.append( chunk )
        if 'l' in fields:
            values.append( len( chunk ) )
        # TODO allow caller to customize the yields
        yield tuple( values )
    debug( 'urlopen_progress', 'R', received, 'r', received_ratio, 't', total )
    result.close()

# TODO enable printing to a different stream
# TODO enable index/total/block interface
def render_progress( caption, ratio, width ): #  index = None, total = None, block = None ):
    """
    Draws a progress bar on the console. First prints a carriage
    return, so this function can be called repeatedly to create an
    "animated" progress bar.

    @param caption: The label printed to the left of the bar.
    @type caption: str

    @param ratio: The percentage progress.
    @type ratio: float

    @param width: The width of the progress bar, in characters.
    @type width: int
    """
    sys.stdout.write( interp( '\r$caption: [' ) )
    thresh = ratio * width
    for cursor in range( width ):
        if cursor < thresh:
            sys.stdout.write( '=' )
        else:
            sys.stdout.write( ' ' )
    sys.stdout.write( interp( '] $ratio' ) )
    if ratio == 1.0:
        sys.stdout.write( '\n' )
    #if index % block == 0:
    #    print interp( '\r$caption: |' )
    #    for counter in range( total / block ):
    #        if counter < index / block:
    #            print '.'
    #        else:
    #            print ' '
    #    print "| "
