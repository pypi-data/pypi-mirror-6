==============
python-delay
==============

Simple decorator stolen from stackoverflow to delay function calls.


Usage
======

from delay import delayed

@delayed(10)
def foo():
    print "wow"

