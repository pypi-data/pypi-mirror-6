What's new
**********


.. whats-new-0.11.1:

What's new in version 0.11.1
============================

The ``past.autotranslate`` feature now works with Python eggs.


.. whats-new-0.11:

What's new in version 0.11
==========================

There are several major new features in version 0.11. 


``past`` package
----------------

The python-future project now provides a ``past`` package in addition to the
``future`` package. Whereas ``future`` provides improved compatibility with
Python 3 code to Python 2, ``past`` provides support for using and interacting
with Python 2 code from Python 3. The structure reflects that of ``future``,
with ``past.builtins`` and ``past.utils``. There is also a new
``past.translation`` package that provides transparent translation of Python 2
code to Python 3. (See below.)

One purpose of ``past`` is to ease module-by-module upgrades to
codebases from Python 2. Another is to help with enabling Python 2 libraries to
support Python 3 without breaking the API they currently provide. (For example,
user code may expect these libraries to pass them Python 2's 8-bit strings,
rather than Python 3's ``bytes`` object.) A third purpose is to help migrate
projects to Python 3 even if one or more dependencies are still on Python 2.

Currently ``past.builtins`` provides forward-ports of Python 2's ``str`` and
``dict`` objects, ``basestring``, and list-producing iterator functions.  In
later releases, ``past.builtins`` will be used internally by the
``past.translation`` package to help with importing and using old Python 2
modules in a Python 3 environment.


Auto-translation of Python 2 modules upon import
------------------------------------------------

``past`` provides an experimental ``translation`` package to help
with importing and using old Python 2 modules in a Python 3 environment.

This is implemented using import hooks that attempt to automatically
translate Python 2 modules to Python 3 syntax and semantics upon import. Use
it like this::

    $ pip3 install plotrique==0.2.5-7 --no-compile   # to ignore SyntaxErrors
    $ python3
    
Then pass in a whitelist of module name prefixes to the ``past.autotranslate()``
function. Example::
    
    >>> from past import autotranslate
    >>> autotranslate('plotrique')
    >>> import plotrique


This is intended to help you migrate to Python 3 without the need for all
your code's dependencies to support Python 3 yet. It should be used as a
last resort; ideally Python 2-only dependencies should be ported
properly to a Python 2/3 compatible codebase using a tool like
``futurize`` and the changes should be pushed to the upstream project.

For more information, see :ref:`translation`.


Separate ``pasteurize`` script
------------------------------

The functionality from ``futurize --from3`` is now in a separate script called
``pasteurize``. Use ``pasteurize`` when converting from Python 3 code to Python
2/3 compatible source. For more information, see :ref:`backwards-conversion`.


pow()
-----

There is now a ``pow()`` function in ``future.builtins.misc`` that behaves like
the Python 3 ``pow()`` function when raising a negative number to a fractional
power (returning a complex number).


input() no longer disabled globally on Py2
------------------------------------------

Previous versions of ``future`` deleted the ``input()`` function from
``__builtin__`` on Python 2 as a security measure. This was because
Python 2's ``input()`` function allows arbitrary code execution and could
present a security vulnerability on Python 2 if someone expects Python 3
semantics but forgets to import ``input`` from ``future.builtins``. This
behaviour has been reverted, in the interests of broadening the
compatibility of ``future`` with other Python 2 modules.

Please remember to import ``input`` from ``future.builtins`` if you use
``input()`` in a Python 2/3 compatible codebase.


Deprecated feature: auto-installation of standard-library import hooks
----------------------------------------------------------------------

Previous versions of ``python-future`` installed import hooks automatically upon
``from future import standard_library``. This has been deprecated in order to
improve robustness and compatibility with modules like ``requests`` that already
perform their own single-source Python 2/3 compatibility.

.. (Previously, the import hooks were
.. bleeding into surrounding code, causing incompatibilities with modules like
.. ``requests`` (issue #19). 

In the next version of ``python-future``, importing ``future.standard_library``
will no longer install import hooks by default. Instead, please install the
import hooks explicitly as follows::
    
    from future import standard_library
    standard_library.install_hooks()

and uninstall them after your import statements using::

    standard_library.remove_hooks()

..  For more fine-grained use of import hooks, the names can be passed explicitly as
..  follows::
.. 
..      from future import standard_library
..      standard_library.install_hooks()


*Note*: this will be a backward-incompatible change.

.. This feature may be resurrected in a later version if a safe implementation can be found.


Internal changes
----------------

The internal ``future.builtins.backports`` module has been renamed to
``future.builtins.types``. This will change the ``repr`` of ``future``
types but not their use.


.. whats-new-0.10.2:

What's new in version 0.10.2
============================

New context manager for standard_library hooks
----------------------------------------------

``future.standard_library`` provides a new context manager called
``hooks``. Use it as follows::

    >>> from future import standard_library
    >>> with standard_library.hooks():
    ...     import queue
    ...     import socketserver
    ...     from http.client import HTTPConnection
    >>> import requests
    >>> # etc.

``future.standard_library`` also supports explicit calls to the
``install_hooks`` and ``remove_hooks`` functions as an alternative.

.. If you prefer, the following imports are also available directly::
.. 
..     >>> from future.standard_library import queue
..     >>> from future.standard_library import socketserver
..     >>> from future.standard_library.http.client import HTTPConnection


As usual, this feature has no effect on Python 3.


.. Simpler imports
.. ---------------
.. 
.. It is now possible to import builtins directly from the ``future``
.. namespace as follows::
.. 
..     >>> from future import *
..     
.. or just those you need::
.. 
..     >>> from future import open, str


Utility functions for raising exceptions with a traceback portably
------------------------------------------------------------------

The functions ``raise_with_traceback()`` and ``raise_`` were added to
``future.utils`` to offer either the Python 3.x or Python 2.x behaviour
for raising exceptions. Thanks to Joel Tratner for the contribution of
these.


.. whats-new-0.10:

What's new in version 0.10
==========================

Backported ``dict`` type
------------------------

``future.builtins`` now provides a Python 2 ``dict`` subclass whose
:func:`keys`, :func:`values`, and :func:`items` methods produce
memory-efficient iterators. On Python 2.7, these also have the same set-like
view behaviour as on Python 3. This can streamline code needing to iterate
over large dictionaries. For example::

    from __future__ import print_function
    from future.builtins import dict, range
    
    squares = dict({i: i**2 for i in range(10**7)})

    assert not isinstance(d.items(), list)
    # Because items() is memory-efficient, so is this:
    square_roots = dict((i_squared, i) for (i, i_squared) in squares.items())

For more information, see :ref:`dict-object`.


Refactoring of standard_library hooks (v0.10.2)
-----------------------------------------------

There is a new context manager ``future.standard_library.hooks``. Use it like
this::

    from future import standard_library
    with standard_library.hooks():
        import queue
        import configserver
        # etc.

If not using this decorator, it is now encouraged to add an explicit call to
``standard_library.install_hooks()`` as follows::

    from future import standard_library
    standard_library.install_hooks()
    
    import queue
    import html
    import http.client
    # etc.

and to remove the hooks afterwards with::

    standard_library.remove_hooks()

The functions ``install_hooks()`` and ``remove_hooks()`` were previously
called ``enable_hooks()`` and ``disable_hooks()``. The old names are
still available as aliases, but are deprecated.


Utility functions raise_ and exec_
----------------------------------

The functions ``raise_with_traceback()`` and ``raise_()`` were
added to ``future.utils`` to offer either the Python 3.x or Python 2.x
behaviour for raising exceptions. Thanks to Joel Tratner for the
contribution of these. ``future.utils.reraise()`` is now deprecated.

A portable ``exec_()`` function has been added to ``future.utils`` from
``six``.


Bugfixes
--------
- Fixed newint.__divmod__
- Improved robustness of installing and removing import hooks in :mod:`future.standard_library`
- v0.10.1: Fixed broken ``pip install future`` on Py3


.. whats-new-0.9:

What's new in version 0.9.x
===========================


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
