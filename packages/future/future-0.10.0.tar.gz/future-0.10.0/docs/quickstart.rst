.. _quickstart-guide:

Quick-start guide
=================

You can use ``future`` to help to port your code from Python 2 to Python 3
today -- and still have it run on Python 2.

If you already have Python 3 code, you can instead use ``future`` to
offer Python 2 compatibility with almost no extra work.

Installation
------------

To install the latest stable version, type::

    pip install future

If you would prefer the latest development version, it is available `here <https://github.com/PythonCharmers/python-future>`_.


If you are writing code from scratch
------------------------------------

Start each module with these lines::

    from __future__ import (absolute_import, division,
                            print_function, unicode_literals)
    from future import standard_library
    from future.builtins import *

Then write standard Python 3 code. The :mod:`future` package will
provide support for running your code on Python 2.6 and 2.7 mostly unchanged.

See :ref:`what-else` for more details.


To convert existing Python 3 code
---------------------------------

To offer backward compatibility with Python 2, you can use the ``futurize``
script with the ``--from3`` parameter. This adds these lines at the top of each
module::

    from __future__ import (absolute_import, division,
                            print_function, unicode_literals)
    from future import standard_library
    from future.builtins import *
    
and converts a few Python 3-only constructs to a form compatible with
both Py3 and Py2. Most remaining Python 3 code should simply work on
Python 2.

For a realistic example, you can see the included `backported
http.client module
<https://github.com/PythonCharmers/python-future/blob/master/future/standard_library/http/client.py>`_,
and look at the diff between this and the Python 3.3 module (e.g.
``/usr/lib/python3.3/http/client.py``). 
 
See :ref:`backwards-conversion` for more details.


To convert existing Python 2 code
---------------------------------

Start with the :ref:`automatic-conversion` page.

.. If you already know Python 3, start with the :ref:`automatic-conversion` page.
.. If you don't know Python 3 yet, start with :ref:`python3-essentials`.


.. _standard-library:

Standard library reorganization
-------------------------------

:mod:`future` supports the standard library reorganization (PEP 3108)
via import hooks, allowing almost all moved standard library modules to
be accessed under their Python 3 names and locations in Python 2::
    
    from future import standard_library
    
    import socketserver
    import queue
    import configparser
    import test.support
    import html.parser
    from collections import UserList
    from itertools import filterfalse, zip_longest
    from http.client import HttpConnection
    # and other moved modules and definitions

:mod:`future` also includes backports for these stdlib modules from Py3
that were heavily refactored versus Py2::
    
    import html
    import html.entities
    import html.parser

    import http
    import http.client
    import http.server

These modules are currently not supported, but we aim to support them in
the future::
    
    import http.cookies
    import http.cookiejar

    import urllib
    import urllib.parse
    import urllib.request
    import urllib.error

If you need one of these, please open an issue `here
<https://github.com/PythonCharmers/python-future>`_.

For more information on interfaces that have changed in the standard library
between Python 2 and Python 3, see :ref:`stdlib-incompatibilities`.


.. _utilities-guide:

Utilities
---------

:mod:`future` also provides some useful functions and decorators to ease
backward compatibility with Py2 in the :mod:`future.utils` module. These
are a selection of the most useful functions from ``six`` and various
home-grown Py2/3 compatibility modules from various Python projects,
such as Jinja2, Pandas, IPython, and Django.

Examples::

    # Functions like print() expect __str__ on Py2 to return a byte
    # string. This decorator maps the __str__ to __unicode__ on Py2 and
    # defines __str__ to encode it as utf-8:

    from future.utils import python_2_unicode_compatible

    @python_2_unicode_compatible
    class MyClass(object):
        def __str__(self):
            return u'Unicode string: \u5b54\u5b50'
    a = MyClass()

    # This then prints the Chinese characters for Confucius:
    print(a)


    # Iterators on Py3 require a __next__() method, whereas on Py2 this
    # is called next(). This decorator allows Py3-style iterators to work
    # identically on Py2:

    @implements_iterator
    class Upper(object):
        def __init__(self, iterable):
            self._iter = iter(iterable)
        def __next__(self):                 # note the Py3 interface
            return next(self._iter).upper()
        def __iter__(self):
            return self

    print(list(Upper('hello')))
    # prints ['H', 'E', 'L', 'L', 'O']

On Python 3 these decorators are no-ops.


For more information, see :ref:`what-else`.

