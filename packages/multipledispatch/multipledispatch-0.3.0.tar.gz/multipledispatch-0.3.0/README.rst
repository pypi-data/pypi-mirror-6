Multiple Dispatch
=================

|Build Status|

A relatively sane approach to multiple dispatch in Python.

There exists several implementations of multiple dispatch (see links below).
This implementation is efficient, relatively complete, and performs static
analysis to avoid common issues.

Example
-------

.. code-block:: python

   >>> from multipledispatch import dispatch

   >>> @dispatch(int, int)
   ... def add(x, y):
   ...     return x + y

   >>> @dispatch(object, object)
   ... def add(x, y):
   ...     return "%s + %s" % (x, y)

   >>> add(1, 2)
   3

   >>> add(1, 'hello')
   '1 + hello'

What this does
--------------

-  Dispatches on all non-keyword arguments

-  Supports inheritance

-  Supports instance methods

-  Supports union types, e.g. ``(int, float)``

-  Supports builtin abstract classes, e.g. ``Iterator, Number, ...``

-  Caches for fast repeated lookup

-  Identifies possible ambiguities at function definition time

-  Provides hints to resolve ambiguities when they occur

What this doesn't do
--------------------

-  Vararg dispatch

.. code-block:: python

   @dispatch([int])
   def add(*args):
       ...

-  Diagonal dispatch

.. code-block:: python

   a = arbitrary_type()
   @dispatch(a, a)
   def are_same_type(x, y):
       return True

-  Respect namespaces


Installation and Dependencies
-----------------------------

``multipledispatch`` is on the Python Package Index (PyPI):

::

    pip install multipledispatch

or

::

    easy_install multipledispatch


``multipledispatch`` supports Python 2.6+ and Python 3.2+ with a common
codebase.  It is pure Python and requires no dependencies beyond the standard
library.

It is, in short, a light weight dependency.


License
-------

New BSD. See License_.


Links
-----

-  `Five-minute Multimethods in Python by
   Guido <http://www.artima.com/weblogs/viewpost.jsp?thread=101605>`__
-  ```multimethods`` package on
   PyPI <https://pypi.python.org/pypi/multimethods>`__
-  `Clojure Protocols <http://clojure.org/protocols>`__
-  `Julia methods
   docs <http://julia.readthedocs.org/en/latest/manual/methods/>`__
-  `Karpinksi notebook: *The Design Impact of Multiple
   Dispatch* <http://nbviewer.ipython.org/gist/StefanKarpinski/b8fe9dbb36c1427b9f22>`__
-  `Wikipedia
   article <http://en.wikipedia.org/wiki/Multiple_dispatch>`__

.. |Build Status| image:: https://travis-ci.org/mrocklin/multipledispatch.png
   :target: https://travis-ci.org/mrocklin/multipledispatch
.. _License: https://github.com/pymultipledispatch/multipledispatch/blob/master/LICENSE.txt
