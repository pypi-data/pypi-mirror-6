What's new
**********


.. whats-new-0.10:

What's new in version 0.10
==========================

More robust implementation of standard_library.disable_hooks() and enable_hooks()
---------------------------------------------------------------------------------

Backported ``dict`` type
------------------------

``future.builtins`` now provides a Python 2 ``dict`` subclass whose
:func:`keys`, :func:`values`, and :func:`items` methods produce
memory-efficient iterators. On Python 2.7, these also have the same set-like
view behaviour as on Python 3. This can streamline code needing to iterate over
large dictionaries. For example::

    from __future__ import print_function
    from future.builtins import dict, range
    
    squares = dict({i: i**2 for i in range(10**7)})

    assert not isinstance(d.items(), list)
    # Because items() is memory-efficient, so is this:
    square_roots = dict((i_squared, i) for (i, i_squared) in squares.items())

For more information, see :ref:`dict-object`.

Bugfixes
--------
- To newint.__divmod__


.. whats-new-0.9:

What's new in version 0.9
=========================


``isinstance`` checks supported natively with backported types
--------------------------------------------------------------

The ``isinstance`` function is no longer redefined in ``future.builtins``
to operate with the backported ``int``, ``bytes`` and ``str``.
``isinstance`` checks with the backported types now work correctly by
default; we achieve this through overriding the ``__instancecheck__``
method of metaclasses of the backported types.

For more information, see :ref:`isinstance-calls`.


``futurize``: minimal imports by default
----------------------------------------

By default, the ``futurize`` script now only adds the minimal set of
imports deemed necessary.

There is now an ``--all-imports`` option to the ``futurize`` script which
gives the previous behaviour, which is to add all ``__future__`` imports
and ``from future.builtins import *`` imports to every module. (This even
applies to an empty ``__init__.py`` file.


Looser type-checking for the backported ``str`` object
------------------------------------------------------

Now the ``future.builtins.str`` object behaves more like the Python 2
``unicode`` object with regard to type-checking. This is to work around some
bugs / sloppiness in the Python 2 standard library involving mixing of
byte-strings and unicode strings, such as ``os.path.join`` in ``posixpath.py``.

``future.builtins.str`` still raises the expected ``TypeError`` exceptions from
Python 3 when attempting to mix it with ``future.builtins.bytes``.


suspend_hooks() context manager added to ``future.standard_library``
--------------------------------------------------------------------

Pychecker (as of v0.6.1)'s ``checker.py`` attempts to import the ``builtins``
module as a way of determining whether Python 3 is running. Since this
succeeds when ``from future import standard_library`` is in effect, this
check does not work and pychecker sets the wrong value for its internal ``PY2``
flag is set.

To work around this, ``future`` now provides a context manager called
``suspend_hooks`` that can be used as follows::

    from future import standard_library
    ...
    with standard_library.suspend_hooks():
        from pychecker.checker import Checker


.. whats-new-0.8:

What's new in version 0.8
=========================

Python 2.6 support
------------------

``future`` now includes support for Python 2.6.

To run the ``future`` test suite on Python 2.6, this additional package is needed::

    pip install unittest2

``http.server`` also requires the ``argparse`` package::

    pip install argparse


Unused modules removed
----------------------

The ``future.six`` module has been removed. ``future`` doesn't require ``six``
(and hasn't since version 0.3). If you need support for Python versions before
2.6, ``six`` is the best option. ``future`` and ``six`` can be installed
alongside each other easily if needed.

The unused ``hacks`` module has also been removed from the source tree.


isinstance() added to :mod:`future.builtins` (v0.8.2)
-----------------------------------------------------

It is now possible to use ``isinstance()`` calls normally after importing ``isinstance`` from 
``future.builtins``. On Python 2, this is specially defined to be compatible with
``future``'s backported ``int``, ``str``, and ``bytes`` types, as well as
handling Python 2's int/long distinction.

The result is that code that uses ``isinstance`` to perform type-checking of
ints, strings, and bytes should now work identically on Python 2 as on Python 3.

The utility functions ``isint``, ``istext``, and ``isbytes`` provided before for
compatible type-checking across Python 2 and 3 in :mod:`future.utils` are now
deprecated.


.. changelog:

Summary of all changes
======================

v0.10:
  * New backported ``dict`` object with set-like ``keys``, ``values``, ``items``

v0.9:
  * :func:`isinstance` hack removed in favour of ``__instancecheck__`` on the
    metaclasses of the backported types
  * ``futurize`` now only adds necessary imports by default
  * Looser type-checking by ``future.builtins.str`` when combining with Py2
    native byte-strings.

v0.8.3:
  * New ``--all-imports`` option to ``futurize``
  * Fix bug with ``str.encode()`` with encoding as a non-keyword arg

v0.8.2:
  * New ``isinstance`` function in :mod:`future.builtins`. This obviates
    and deprecates the utility functions for type-checking in :mod:`future.utils`.

v0.8.1:
  * Backported ``socketserver.py``. Fixes sporadic test failures with
    ``http.server`` (related to threading and old-style classes used in Py2.7's
    ``SocketServer.py``).

  * Move a few more safe ``futurize`` fixes from stage2 to stage1

  * Bug fixes to :mod:`future.utils`
  
v0.8:
  * Added Python 2.6 support

  * Removed unused modules: :mod:`future.six` and :mod:`future.hacks`

  * Removed undocumented functions from :mod:`future.utils`

v0.7:
  * Added a backported Py3-like ``int`` object (inherits from long).

  * Added utility functions for type-checking and docs about
    ``isinstance`` uses/alternatives.

  * Fixes and stricter type-checking for bytes and str objects

  * Added many more tests for the ``futurize`` script

  * We no longer disable obsolete Py2 builtins by default with ``from
    future.builtins import *``. Use ``from future.builtins.disabled
    import *`` instead.

v0.6:
  * Added a backported Py3-like ``str`` object (inherits from Py2's ``unicode``)

  * Removed support for the form ``from future import *``: use ``from future.builtins import *`` instead

v0.5.3:
  * Doc improvements

v0.5.2:
  * Add lots of docs and a Sphinx project

v0.5.1:
  * Upgraded included ``six`` module (included as ``future.utils.six``) to v1.4.1

  * :mod:`http.server` module backported

  * bytes.split() and .rsplit() bugfixes

v0.5.0:
  * Added backported Py3-like ``bytes`` object

v0.4.2:
  * Various fixes

v0.4.1:
  * Added :func:`open` (from :mod:`io` module on Py2)
  * Improved docs

v0.4.0:
  * Added various useful compatibility functions to :mod:`future.utils`

  * Reorganized package: moved all builtins to :mod:`future.builtins`; moved
    all stdlib things to ``future.standard_library``

  * Renamed ``python-futurize`` console script to ``futurize``

  * Moved ``future.six`` to ``future.utils.six`` and pulled the most relevant
    definitions to :mod:`future.utils`.

  * More improvements to "Py3 to both" conversion (``futurize.py --from3``)

v0.3.5:
  * Fixed broken package setup ("package directory 'libfuturize/tests' does not exist")

v0.3.4:
  * Added ``itertools.zip_longest``

  * Updated 2to3_backcompat tests to use futurize.py

  * Improved libfuturize fixers: correct order of imports; add imports only when necessary (except absolute_import currently)

v0.3.3:
  * Added ``python-futurize`` console script

  * Added ``itertools.filterfalse``

  * Removed docs about unfinished backports (urllib etc.)

  * Removed old Py2 syntax in some files that breaks py3 setup.py install

v0.3.2:
  * Added test.support module

  * Added UserList, UserString, UserDict classes to collections module

  * Removed ``int`` -> ``long`` mapping
  
  * Added backported ``_markupbase.py`` etc. with new-style classes to fix travis-ci build problems

  * Added working ``html`` and ``http.client`` backported modules
v0.3.0:
  * Generalized import hooks to allow dotted imports

  * Added backports of ``urllib``, ``html``, ``http`` modules from Py3.3 stdlib using ``future``

  * Added ``futurize`` script for automatically turning Py2 or Py3 modules into
    cross-platform Py3 modules

  * Renamed ``future.standard_library_renames`` to
    ``future.standard_library``. (No longer just renames, but backports too.)

v0.2.2.1:
  * Small bug fixes to get tests passing on travis-ci.org

v0.2.1:
  * Small bug fixes

v0.2.0:
  * Features module renamed to modified_builtins

  * New functions added: :func:`round`, :func:`input`

  * No more namespace pollution as a policy::

        from future import *

    should have no effect on Python 3. On Python 2, it only shadows the
    builtins; it doesn't introduce any new names.

  * End-to-end tests with Python 2 code and 2to3 now work

v0.1.0:
  * first version with tests!

  * removed the inspect-module magic

v0.0.x:
  * initial releases. Use at your peril.
