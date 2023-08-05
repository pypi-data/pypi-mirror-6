============
PyPy Support
============

PyPy is a Python implementation done in Python. It uses a JIT compiler
and is typically faster than CPython for many things.

As PyPy is *not* CPython, the Couchbase extension must go through an
experimental PyPy layer known as `cpyext`.

The stability and featureset of this extension under PyPy is limited by the
stability or instability of the `cpyext` implementation within PyPy.

Here are the things known to work:

    * Basic Get/Set operations
    * Multi operations
    * Views

Here are the things not known to work:

    * Twisted Support
    * Gevent support (even if PyPy did theoretically support gevent)
    * Threading support (i.e. ``unlock_gil`` is always false)
