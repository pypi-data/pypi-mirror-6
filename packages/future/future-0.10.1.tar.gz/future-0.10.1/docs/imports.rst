.. _imports:

Imports
=======

future imports
~~~~~~~~~~~~~~

The imports to include at the top of every Py2/3-compatible module using
``future`` are::

    from __future__ import (absolute_import, division,
                            print_function, unicode_literals)
    from future import standard_library
    from future.builtins import *

On Python 3, these import lines have zero effect and zero namespace
pollution.

On Python 2, ``from future import standard_library`` installs
import hooks to allow renamed and moved standard library modules to be
imported from their new Py3 locations. See :ref:`standard-library` for more
information.

On Python 2, the ``from future.builtins import *`` line shadows builtins
to provide their Python 3 semantics. (See :ref:`explicit-imports` for the
explicit form.)


__future__ imports
~~~~~~~~~~~~~~~~~~

For more information about the ``__future__`` imports, which are a
standard feature of Python, see the following docs:

- absolute_import: `PEP 328: Imports: Multi-Line and Absolute/Relative <http://www.python.org/dev/peps/pep-0328>`_
- division: `PEP 238: Changing the Division Operator <http://www.python.org/dev/peps/pep-0238>`_
- print_function: `PEP 3105: Make print a function <http://www.python.org/dev/peps/pep-3105>`_
- unicode_literals: `PEP 3112: Bytes literals in Python 3000 <http://www.python.org/dev/peps/pep-3112>`_

These are all available in Python 2.6 and up, and enabled by default in Python 3.x.


.. _explicit-imports:

Explicit imports
~~~~~~~~~~~~~~~~

If you prefer explicit imports, the explicit equivalent of the ``from
future.builtins import *`` line is::

    from future.builtins import (filter, map, zip,
                                 ascii, chr, hex, input, oct, open,
                                 bytes, int, range, round, str, super)


The disadvantage of importing only some of these builtins is that it
increases the risk of introducing Py2/3 portability bugs as your code
evolves over time.

To understand the details of these functions on Python 2, see the docs
for these modules:

- future.builtins
- future.builtins.iterators
- future.builtins.misc
- future.builtins.backports

The internal API is currently as follows::

    from future.builtins.iterators import filter, map, zip
    from future.builtins.misc import ascii, chr, hex, input, oct, open
    from future.builtins.backports import bytes, int, range, round, str, super

(Please note that this internal API is evolving and may not be stable
between different versions of ``future``.)


.. _obsolete-builtins:

Obsolete Python 2 builtins
~~~~~~~~~~~~~~~~~~~~~~~~~~

Twelve Python 2 builtins have been removed from Python 3. To aid with
porting code to Python 3 module by module, you can use the following
import to cause a ``NameError`` exception to be raised on Python 2 as
on Python 3 when any of the obsolete builtins is used::

    from future.builtins.disabled import *

This is equivalent to::

    from future.builtins.disabled import (apply, cmp, coerce, execfile,
                                 file, long, raw_input, reduce, reload,
                                 unicode, xrange, StandardError)

Running ``futurize`` over code that uses these Python 2 builtins replaces
them with their Python 3 equivalents (which work on Py2 as well using
``future`` imports.)

