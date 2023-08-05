
hexdump: edit your binary with any text editor


Cross-platform Python 2/3 library to dump and restore
binary data to and from hex form.

Placed into public domain
by anatoly techtonik <techtonik@gmail.com>


01 - dump binary data string
============================

Python 2::

    >>> import hexdump
    >>> hexdump.hexdump('\x00'*16)
    00000000: 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ................

Python 3::

   >>> import hexdump
   >>> hexdump.hexdump('\x00'*16)
   ...
   TypeError: Abstract unicode data (expected bytes)
   >>> hexdump.hexdump(b'\x00'*16)
   00000000: 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ................
 
Python 3 strings are arrays of abstract indexes in unicode
table. Single index is an integer which takes more than one
byte when stored, so you need to specify exactly how to store
these bytes with encoding.


02 - restore binary data from hex dump string
==============================================

Python 2::

   >>> import hexdump
   >>> res = hexdump.restore(
   ... '0010: 00 11 22 33 44 55 66 77  88 99 AA BB CC DD EE FF  .."3DUfw........')
   >>> res
   '\x00\x11"3DUfw\x88\x99\xaa\xbb\xcc\xdd\xee\xff'
   >>> type(res)
   <type 'str'>

Python 3::

   >>> import hexdump
   >>> res = hexdump.restore(
   ... '0010: 00 11 22 33 44 55 66 77  88 99 AA BB CC DD EE FF  .."3DUfw........')
   >>> res
   b'\x00\x11"3DUfw\x88\x99\xaa\xbb\xcc\xdd\xee\xff'
   >>> type(res)
   <class 'bytes'>


03 - use as command line tool
=============================
Make hex dump of binary data::

   $ python hexdump.py binary.dat > hexdump.txt
   # or
   $ python -m hexdump binary.dat
   0000000000: 00 00 00 5B 68 65 78 64  75 6D 70 5D 00 00 00 00  ...[hexdump]....
   0000000010: 00 11 22 33 44 55 66 77  88 99 AA BB CC DD EE FF  .."3DUfw........

Restore binary data::

   $ python -m hexdump --restore hexdump.txt > binary.dat


04 - run self-tests
===================
Automatically with `tox`::

   $ tox

Manually::

   $ hexdump.py --test output.txt
   $ diff -u3 hextest.txt output.txt


ChangeLog
=========
1.0 (2013-12-30)
 * length of address is reduced from 10 to 8
 * hexdump() got new 'result' keyword argument, it
   can be either 'print', 'generator' or 'return'
 * actual dumping logic is now in new dumpgen()
   generator function
 * new dump(binary) function that takes binary data
   and returns string like "66 6F 72 6D 61 74"
 * new genchunks(mixed, size) function that chunks
   both sequences and file like objects

0.5 (2013-06-10)
 * hexdump is now also a command line utility (no
   restore yet)

0.4 (2013-06-09)
 * fix installation with Python 3 for non English
   versions of Windows, thanks to George Schizas

0.3 (2013-04-29)
 * fully Python 3 compatible

0.2 (2013-04-28)
 * restore() to recover binary data from a hex dump in
   native, Far Manager and Scapy text formats (others
   might work as well)
 * restore() is Python 3 compatible

0.1 (2013-04-28)
 * working hexdump() function for Python 2


Release checklist
=================

| [ ] run tests  
| [ ] update version in hexdump.py  
| [x] update version in setup.py  
| [ ] update ChangeLog in README.txt from hexdump.py  
| [ ] python setup.py register sdist upload  
