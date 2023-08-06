#!/usr/bin/env python

from commons import sqlhash
from shelve import *
d = Shelf(sqlhash.SQLhash('/tmp/sh',flags='n'),protocol=2,writeback=1)
d['maxuid']=0
d.close()
d = Shelf(sqlhash.SQLhash('/tmp/sh',flags='r'),protocol=2)
print d['maxuid']
