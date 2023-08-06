.. _automatic-conversion:

Automatic conversion to Py2/3 with ``futurize`` and ``pasteurize``
==================================================================

The ``future`` source tree includes scripts called ``futurize`` and
``pasteurize`` to aid in making Python 2 code or Python 3 code compatible with
both platforms (Py2&3) using the :mod:`future` module. It is based on 2to3 and
uses fixers from ``lib2to3``, ``lib3to2``, and ``python-modernize``.

``futurize`` passes Python 2 code through all the appropriate fixers to turn it
into valid Python 3 code, and then adds ``__future__`` and ``future`` package
imports.

For conversions from Python 3 code to Py2/3, use the ``pasteurize`` script
instead. This converts Py3-only constructs (e.g. new metaclass syntax) and adds
``__future__`` and ``future`` imports to the top of each module.

In both cases, the result should be relatively clean Py3-style code that runs
mostly unchanged on both Python 2 and Python 3.

.. _forwards-conversion:

Futurize: 2 to both
--------------------

For example, running ``futurize`` turns this Python 2 code::
    
    import ConfigParser

    class Blah(object):
        pass
    print 'Hello',

into this code which runs on both Py2 and Py3::
    
    from __future__ import print_function
    from future import standard_library
    
    import configparser

    class Blah(object):
        pass
    print('Hello', end=' ')


To write out all the changes to your Python files that ``futurize`` suggests,
use the ``-w`` flag.

For complex projects, it may be better to divide the porting into two stages.
Stage 1 is for "safe" changes that modernize the code but do not break Python
2.6 compatibility or introduce a depdendency on the ``future`` package. Stage 2
is to complete the process.


.. _forwards-conversion-stage1:

Stage 1: "safe" fixes
~~~~~~~~~~~~~~~~~~~~~

Run with::

	futurize --stage1

This applies fixes that modernize Python 2 code without changing the effect of
the code. With luck, this will not introduce any bugs into the code, or will at
least be trivial to fix. The changes are those that bring the Python code
up-to-date without breaking Py2 compatibility. The resulting code will be
modern Python 2.6-compatible code plus ``__future__`` imports from the
following set::

    from __future__ import absolute_import
    from __future__ import division
    from __future__ import print_function

Only those ``__future__`` imports deemed necessary will be added unless
the ``--all-imports`` command-line option is passed to ``futurize``, in
which case they are all added.

The ``from __future__ import unicode_literals`` declaration is not added
unless the ``--unicode-literals`` flag is passed to ``futurize``.

The changes include::

    - except MyException, e:
    + except MyException as e:
    
    - print >>stderr, "Blah"
    + from __future__ import print_function
    + print("Blah", stderr)

Implicit relative imports fixed, e.g.::

    - import mymodule
    + from __future__ import absolute_import
    + from . import mymodule

.. and all unprefixed string literals '...' gain a b prefix to be b'...'.

.. (This last step can be prevented using --no-bytes-literals if you already have b'...' markup in your code, whose meaning would otherwise be lost.)

Stage 1 does not add any imports from the ``future`` package. The output of
stage 1 will probably not (yet) run on Python 3. 

The goal for this stage is to create most of the ``diff`` for the entire
porting process, but without introducing any bugs. It should be uncontroversial
and safe to apply to every Python 2 package. The subsequent patches introducing
Python 3 compatibility should then be shorter and easier to review.


.. _forwards-conversion-stage2:

Stage 2: Py3-style code with ``future`` wrappers for Py2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run with::

    futurize —-stage2 myfolder/*.py

This stage adds a dependency on the ``future`` package. The goal for stage 2 is
to make further mostly safe changes to the Python 2 code to use Python 3-style
code that then still runs on Python 2 with the help of the appropriate builtins
and utilities in ``future``.

For example::

    name = raw_input('What is your name?\n')

    for k, v in d.iteritems():
        assert isinstance(v, basestring)

    class MyClass(object):
        def __unicode__(self):
            return u'My object'
        def __str__(self):
            return unicode(self).encode('utf-8')

would be converted by Stage 2 to this code::

    from future.builtins import input
    from future.builtins import str
    from future.utils import iteritems, python_2_unicode_compatible

    name = input('What is your name?\n')

    for k, v in iteritems(d):
        assert isinstance(v, (str, bytes))

    @python_2_unicode_compatible
    class MyClass(object):
        def __str__(self):
            return u'My object'

Stage 2 also renames standard-library imports to their Py3 names and adds these
two lines::

    from future import standard_library
    standard_library.install_hooks()

For example::

    import ConfigParser

becomes::
    
    from future import standard_library
    standard_library.install_hooks()
    import ConfigParser


Ideally the output of this stage should not be a ``SyntaxError`` on either
Python 3 or Python 2.

After this, you can run your tests on Python 3 and make further code changes
until they pass on Python 3.

The next step would be manually adding some decorators from ``future`` to
e-enable Python 2 compatibility. See :ref:`what-else` for more info.



.. _forwards-conversion-text:

Separating text from bytes
~~~~~~~~~~~~~~~~~~~~~~~~~~

After applying stage 2, the recommended step is to decide which of your Python
2 strings represent text and which represent binary data and to prefix all
string literals with either ``b`` or ``u`` accordingly. Furthermore, to ensure
that these types behave similarly on Python 2 as on Python 3, also wrap
byte-strings or text in the ``bytes`` and ``str`` types from ``future``. For
example::
    
    from future.builtins import bytes, str
    b = bytes(b'\x00ABCD')
    s = str(u'This is normal text')

Any unadorned string literals will then represent native platform strings
(byte-strings on Py2, unicode strings on Py3).

An alternative is to pass the ``--unicode_literals`` flag::
  
  $ futurize --unicode_literals mypython2script.py

After runnign this, all string literals that were not explicitly marked up as
``b''`` will mean text (Python 3 ``str`` or Python 2 ``unicode``).


.. _forwards-conversion-stage3:

Post-conversion
~~~~~~~~~~~~~~~

After running ``futurize``, we recommend first getting the tests passing on
Py3, and then on Py2 again with the help of the ``future`` package.


.. _backwards-conversion:

Pasteurize: 3 to both
--------------------

Running ``pasteurize -w mypy3module.py`` turns this Python 3 code::
    
    import configparser
    
    class Blah:
        pass
    print('Hello', end=None)

into this code which runs on both Py2 and Py3::
    
    from __future__ import print_function
    from future import standard_library
    standard_library.install_hooks()
    
    import configparser

    class Blah(object):
        pass
    print('Hello', end=None)

Notice that both ``futurize`` and ``pasteurize`` create explicit new-style
classes that inherit from ``object`` on both Python versions, and both 
refer to stdlib modules (as well as builtins) under their Py3 names.

``pasteurize`` also handles the following Python 3 features:

- keyword-only arguments
- metaclasses (using :func:`~future.utils.with_metaclass`)
- extended tuple unpacking (PEP 3132)

To handle function annotations (PEP 3107), see :ref:`func_annotations`.


How well do ``futurize`` and ``pasteurize`` work?
-------------------------------------------------

They are still incomplete and make some mistakes, like 2to3, on which they are
based.

Nevertheless, ``futurize`` and ``pasteurize`` are useful to automate much of the
work of porting, particularly the boring repetitive text substitutions. They also
help to flag which parts of the code require attention.

Please report bugs on `GitHub
<https://github.com/PythonCharmers/python-future/>`_.

Contributions to the ``lib2to3``-based fixers for ``futurize`` and
``pasteurize`` are particularly welcome! Please see :ref:`contributing`.


.. _futurize-limitations

Known limitations of ``futurize``
---------------------------------

``futurize`` doesn't currently make any of these changes automatically::

1. A source encoding declaration line like::
    
       # -*- coding:utf-8 -*-
  
   is not kept at the top of a file. It must be moved manually back to line 1 to take effect.

2. Strings containing ``\U`` produce a ``SyntaxError`` on Python 3. An example is::

       s = 'C:\Users'.

   Python 2 expands this to ``s = 'C:\\Users'``, but Python 3 requires a raw
   prefix (``r'...'``). This also applies to multi-line strings (including
   multi-line docstrings).


