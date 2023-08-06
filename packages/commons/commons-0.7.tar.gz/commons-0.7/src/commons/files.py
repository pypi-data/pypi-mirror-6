# -*- mode: python; tab-width: 4; indent-tabs-mode: nil; py-indent-offset: 4; -*-
# vim:ft=python:et:sw=4:ts=4

"""
File and directory manipulation.

@var invalid_filename_chars: The characters which are usually
prohibited on most modern file systems.

@var invalid_filename_chars_regex: A regex character class constructed
from L{invalid_filename_chars}.
"""

from __future__ import with_statement

__all__ = '''
soft_makedirs
temp_dir
cleanse_filename
invalid_filename_chars
invalid_filename_chars_regex
disk_double_buffer
versioned_guard
versioned_cache
read_file
write_file
write_or_rm
is_nonempty_file
'''.split()

import os, re, tempfile
from cPickle import *
from commons.path import path

def soft_makedirs( path ):
    """
    Emulate C{mkdir -p} (doesn't complain if it already exists).

    @param path: The path of the directory to create.
    @type path: str

    @raise OSError: If it cannot create the directory. It only
    swallows OS error 17.
    """
    try:
        os.makedirs( path )
    except OSError, ex:
        if ex.errno == 17:
            pass
        else:
            raise

def temp_dir( base_dir_name, do_create_subdir = True ):
    """
    Get a temporary directory without polluting top-level /tmp. This follows
    Ubuntu's conventions, choosing a temporary directory name based on
    the given name plus the user name to avoid user conflicts.

    @param base_dir_name: The "name" of the temporary directory. This
    is usually identifies the purpose of the directory, or the
    application to which the temporary directory belongs. E.g., if joe
    calls passes in C{"ssh-agent"} on a standard Linux/Unix system,
    then the full path of the temporary directory will be
    C{"/tmp/ssh-agent-joe"}.
    @type base_dir_name: str

    @param do_create_subdir: If C{True}, then creates a
    sub-sub-directory within the temporary sub-directory (and returns
    the path to that). The sub-sub-directory's name is randomized
    (uses C{tempfile.mkdtemp}).
    @type do_create_subdir: bool

    @return: The path to the temporary (sub-)sub-directory.
    @rtype: str
    """
    base_dir_name += '-' + os.environ[ 'USER' ]
    base_dir = path( tempfile.gettempdir() ) / base_dir_name
    soft_makedirs( base_dir )
    if do_create_subdir:
        return tempfile.mkdtemp( dir = base_dir )
    else:
        return base_dir

invalid_filename_chars = r'*|\/:<>?'
invalid_filename_chars_regex = r'[*|\\\/:<>?]'

def cleanse_filename( filename ):
    """
    Replaces all problematic characters in a filename with C{"_"}, as
    specified by L{invalid_filename_chars}.

    @param filename: The filename to cleanse.
    @type filename: str
    """
    pattern = invalid_filename_chars_regex
    return re.sub( pattern, '_', filename )

class disk_double_buffer( object ):
    """
    A simple disk double-buffer. One file is for reading, the other is for
    writing, and a facility for swapping the two roles is provided.
    """
    def __init__( self, path_base, do_persist = True ):
        self.paths = map( path, [ path_base + '.0', path_base + '.1' ] )
        self.do_persist = do_persist
        self.switch_status = path( path_base + '.switched' )
        if not do_persist or not self.switch_status.exists():
            self.w, self.r = 0, 1 # default
        else:
            self.w, self.r = 1, 0
        self.reload_files()
    def reload_files( self ):
        self.writer = file( self.paths[ self.w ], 'w' )
        if not self.paths[ self.r ].exists():
            self.paths[ self.r ].touch()
        self.reader = file( self.paths[ self.r ] )
    def switch( self ):
        self.close()
        if self.do_persist:
            if self.w == 0: self.switch_status.touch()
            else:           self.switch_status.remove()
        self.r, self.w = self.w, self.r
        self.reload_files()
    def write( self, x ):
        self.writer.write( x )
    def read( self, len = 8192 ):
        return self.reader.read( len )
    def close( self ):
        self.reader.close()
        self.writer.close()

def versioned_guard(path, fresh_version):
    """
    Maintain a version object.  This is useful for working with versioned
    caches.

    @param path: The path to the file containing the cached version object.
    @type path: str

    @param fresh_version: The actual latest version that the cached version
    should be compared against.
    @type fresh_version: object (any type that can be compared)

    @return: True iff the cached version is obsolete (less than the fresh
    version or doesn't exist).
    @rtype: bool
    """
    cache_version = None
    try:
        with file( path ) as f: cache_version = load(f)
    except IOError, (errno, errstr):
        if errno != 2: raise
    if cache_version is None or fresh_version > cache_version:
        with file( path, 'w' ) as f: dump(fresh_version, f)
        return True
    else:
        return False

def versioned_cache(version_path, fresh_version, cache_path, cache_func):
    """
    If fresh_version is newer than the version in version_path, then invoke
    cache_func and cache the result in cache_path (using pickle).

    Note the design flaw with L{versioned_guard}: the updated version value is
    stored immediately, rather than after updating the cache.

    @param version_path: The path to the file version.
    @type version_path: str

    @param fresh_version: The actual, up-to-date version value.
    @type fresh_version: object (any type that can be compared)

    @param cache_path: The path to the cached data.
    @type cache_path: str

    @param cache_func: The function that produces the fresh data to be cached.
    @type cache_func: function (no arguments)
    """
    if versioned_guard( version_path, fresh_version ):
        # cache obsolete, force-fetch new data
        result = cache_func()
        with file(cache_path, 'w') as f: dump(result, f)
        return result
    else:
        # cache up-to-date (should be available since dlcs-timestamp exists!)
        with file(cache_path) as f: return load(f)

def read_file(path):
    f = file(path)
    try: return f.read()
    finally: f.close()

def write_file(path, contents):
    f = file(path,'w')
    try: f.write(contents)
    finally: f.close()

def write_or_rm(p, contents):
    'Write the file or remove it if contents is empty.'
    p = path(p)
    if contents.strip(): write_file(p, contents)
    elif p.isfile(): p.remove()

def is_nonempty_file(path):
    return path.isfile() and read_file(path).strip() != ''
