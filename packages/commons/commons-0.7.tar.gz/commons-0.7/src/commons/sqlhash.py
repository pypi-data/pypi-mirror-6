# Based on <http://code.activestate.com/recipes/576638/>.

''' Dbm based on sqlite -- Needed to support shelves

Key and values are always stored as bytes. This means that when strings are
used they are implicitly converted to the default encoding before being
stored.

@todo Issues:
    - ??? how to coordinate with whichdb
    - ??? Size of text fields fixed or varchar (do we need blobs)
    - ??? does default encoding affect str-->bytes or PySqlite3 always use UTF-8
    - ??? if pure python overhead and pysqlite overhead is too high, rewrite in C
'''

__all__ = ['error', 'open']

import sqlite3, itertools, collections, sys, shelve, cPickle, threading
if sys.version_info < (3,0):
  from itertools import imap as map

error = sqlite3.DatabaseError

class SQLhash(collections.MutableMapping):

    def __init__(self, filename=':memory:', flags='r', mode=None):
        # XXX add flag/mode handling
        #   c -- create if it doesn't exist
        #   n -- new empty
        #   w -- open existing
        #   r -- readonly

        MAKE_SHELF = 'CREATE TABLE IF NOT EXISTS shelf (key BLOB NOT NULL, value BLOB NOT NULL)'
        MAKE_INDEX = 'CREATE UNIQUE INDEX IF NOT EXISTS keyndx ON shelf (key)'
        self.conn = sqlite3.connect(filename)
        self.conn.text_factory = bytes
        self.conn.execute(MAKE_SHELF)
        self.conn.execute(MAKE_INDEX)
        self.conn.commit()

    def __len__(self):
        GET_LEN =  'SELECT COUNT(*) FROM shelf'
        return self.conn.execute(GET_LEN).fetchone()[0]

    def keys(self):
        return SQLhashKeysView(self)

    def values(self):
        return SQLhashValuesView(self)

    def items(self):
        return SQLhashItemsView(self)

    def __iter__(self):
        return iter(self.keys())

    def __contains__(self, key):
        GET_ITEM = 'SELECT value FROM shelf WHERE key = ?'
        return self.conn.execute(GET_ITEM, (sqlite3.Binary(key),)).fetchone() is not None

    def __getitem__(self, key):
        GET_ITEM = 'SELECT value FROM shelf WHERE key = ?'
        item = self.conn.execute(GET_ITEM, (sqlite3.Binary(key),)).fetchone()
        if item is None:
            raise KeyError(key)
        return str(item[0])

    def __setitem__(self, key, value):       
        ADD_ITEM = 'REPLACE INTO shelf (key, value) VALUES (?,?)'
        self.conn.execute(ADD_ITEM, (sqlite3.Binary(key), sqlite3.Binary(value)))
        self.conn.commit()

    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)
        DEL_ITEM = 'DELETE FROM shelf WHERE key = ?'       
        self.conn.execute(DEL_ITEM, (sqlite3.Binary(key),))
        self.conn.commit()

    def update(self, items=(), **kwds):
        if isinstance(items, collections.Mapping):
            items = items.items()
        items = ((sqlite3.Binary(k),sqlite3.Binary(v)) for k,v in items)
        UPDATE_ITEMS = 'REPLACE INTO shelf (key, value) VALUES (?, ?)'
        self.conn.executemany(UPDATE_ITEMS, items)
        self.conn.commit()
        if kwds:
            self.update(kwds)

    def clear(self):        
        CLEAR_ALL = 'DELETE FROM shelf;  VACUUM;'        
        self.conn.executescript(CLEAR_ALL)
        self.conn.commit()

    def close(self):
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def __del__(self):
        self.close()    

class ListRepr:

    def __repr__(self):
        return repr(list(self))    

class SQLhashKeysView(collections.KeysView, ListRepr):
    
    def __iter__(self):
        GET_KEYS = 'SELECT key FROM shelf ORDER BY ROWID'
        return (str(row[0]) for row in self._mapping.conn.cursor().execute(GET_KEYS))

class SQLhashValuesView(collections.ValuesView, ListRepr):
    
    def __iter__(self):
        GET_VALUES = 'SELECT value FROM shelf ORDER BY ROWID'
        return (str(row[0]) for row in self._mapping.conn.cursor().execute(GET_VALUES))

class SQLhashItemsView(collections.ValuesView, ListRepr):
    
    def __iter__(self):
        GET_ITEMS = 'SELECT key, value FROM shelf ORDER BY ROWID'
        return ((str(k), str(v)) for k,v in
                iter(self._mapping.conn.cursor().execute(GET_ITEMS)))

def open(file=None, *args):
    if file is not None:
        return SQLhash(file)
    return SQLhash()

class Shelf(shelve.Shelf):
  def __init__(self, *args, **okwargs):
    kwargs = okwargs.copy()
    try: del kwargs['cache']
    except KeyError: pass
    shelve.Shelf.__init__(self, *args, **kwargs)
    if not okwargs.get('cache', True): self.cache = None
  def __getitem__(self, k):
    val = lambda: cPickle.loads(self.dict[k])
    if self.cache is None:
      return val()
    else:
      try: return self.cache[k]
      except KeyError: return self.cache.setdefault(k, val())
  def __setitem__(self, key, value):
    if self.cache is not None and self.writeback: self.cache[key] = value
    else: self.dict[key] = cPickle.dumps(value, self._protocol)
  def __delitem__(self, key):
    try:
      del self.dict[key]
    except:
      if not self.writeback: raise
      # If writeback is enabled then it's OK if it's missing in the
      # underlying dict but present in the cache; it just means that
      # we only recently inserted it so it's only in the cache.  If
      # it's not in the cache either then we should end with a
      # KeyError.
      del self.cache[key]
    else:
      # Also make sure it's removed from the cache.
      try: del self.cache[key]
      except KeyError: pass
  def iteritems(self):
    return ((k, cPickle.loads(v)) for k,v in self.dict.items())
  def sync(self):
    if self.cache:
      self.dict.update( (k, cPickle.dumps(v, self._protocol)) for k,v in self.cache.items() )
      self.cache.clear()

# Attempt to make a *safe* background-writeback Shelf is hard.

#class Shelf(shelve.Shelf):
#  def __init__(self, *args, **kwargs):
#    shelve.Shelf.__init__(self, *args, **kwargs)
#    threading.Thread(target = self.syncer_proc).start()
#    self.syncer_queue = Queue.Queue()
#  def syncer_proc(self):
#    while True:
#      cache = self.syncer_queue.get()
#      if cache is None: break
#      self.dict.update( (k, cPickle.dumps(v, self._protocol)) for k,v in self.cache.items() )
#  def __setitem__(self, key, value):
#    if self.writeback: self.cache[key] = value
#    else: self.dict[key] = cPickle.dumps(value, self._protocol)
#  def __delitem__(self, key):
#    try:
#      del self.dict[key]
#    except:
#      del self.cache[key]
#    else:
#      try: del self.cache[key]
#      except KeyError: pass
#  def sync(self):
#    if self.cache:
#      self.syncer_queue.push(self.cache)
#      self.cache = {}
#      with self.syncer_lock:
#        while self.syncer_busy: self.syncer_free.wait()
#      self.dict.update( (k, cPickle.dumps(v, self._protocol)) for k,v in self.cache.items() )

if __name__ in '__main___':
    for d in SQLhash(), SQLhash('example'):
        print(list(d), "start")
        d['abc'] = 'lmno'
        print(d['abc'])    
        d['abc'] = 'rsvp'
        d['xyz'] = 'pdq'
        print(d.items())
        print(d.values())
        print(d.keys())
        print(list(d), 'list')
        d.update(p='x', q='y', r='z')
        print(d.items())
        
        del d['abc']
        try:
            print(d['abc'])
        except KeyError:
            pass
        else:
            raise Exception('oh noooo!')
        
        try:
            del d['abc']
        except KeyError:
            pass
        else:
            raise Exception('drat!')

        print(list(d))
        d.clear()
        print(list(d))
        d.update(p='x', q='y', r='z')
        print(list(d))
        d['xyz'] = 'pdq'

        print()
        d.close()
