==============
python-delay
==============

Simple decorator stolen from stackoverflow to delay function calls.

http://stackoverflow.com/questions/3996083/how-can-i-call-a-function-with-delay-in-python


Usage
======

from delay import delayed

@delayed(10)
def foo():
    print "wow"

