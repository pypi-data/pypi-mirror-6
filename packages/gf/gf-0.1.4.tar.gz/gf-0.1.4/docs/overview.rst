Overview
========

`gf` lets you write generic functions
`generic functions <http://en.wikipedia.org/wiki/Generic_function>`_
with multi-methods, that dispatch on all their arguments.


Simple Example
--------------

>>> from gf import generic, method
>>> add = generic()
>>> type(add)
<type 'function'>

Lets define `add` for two integers:

>>> @method(int, int)
... def add(n0, n1):
...     return n0 + n1

Lets test it:

>>> add(1, 2)
3

Calling `add` with instances of other types fails:

>>> add("Hello ", "World")
Traceback (most recent call last):
...
NotImplementedError: Generic '__main__.add' has no implementation for type(s): __builtin__.str, __builtin__.str

Of course `add` can also by defined for two strings:

>>> @method(basestring, basestring)
... def add(s0, s1):
...     return s0 + s1

Now our hello world example works:

>>> add("Hello ", "World")
'Hello World'

`add` can also be defined for a string and an integer:

>>> @method(basestring, int)
... def add(s, n):
...     return s + str(n)

Thus we can add a string and a number:

>>> add("You ", 2)
'You 2'

Python's Special Methods
------------------------

:class:`gf.Object` implements (nearly) all of the `special instance
methods of a python object`_ as a generic function.
The package includes a rational number implementation that makes
heavy use of this feature:

.. code:: python

    @method(object, Rational)
    def __add__(a, b):
        """Add an object and a rational number.
        
        `a` is converted to a :class:`Rational` and then both are added."""
        return Rational(a) + b

    @method(Rational, object)
    def __add__(a, b):
        """Add a rational number and an object.

        `b` is converted to a :class:`Rational` and then both are added."""
        return a + Rational(b)

:class:`gf.Object` also has a more Smalltalk means of overwriting
:meth:`object.__str__` and :meth:`object.__repr__` using a file like object.
Again the rational example is instructive about its usage.

.. code:: python

    @method(Rational, Writer)
    def __out__(rational, writer):
        """Write a nice representation of the rational.
        
        Denominators that equal 1 are not printed."""
        writer("%d", rational.numerator)
        if rational.denominator != 1:
            writer(" / %d", rational.denominator)

    @method(Rational, Writer)
    def __spy__(rational, writer):
        """Write a debug representation of the rational."""
        writer("%s(", rational.__class__.__name__)
        if rational.numerator != 0:
                writer("%r", rational.numerator)
                if rational.denominator != 1:
                    writer(", %r", rational.denominator)
        writer(")")

.. _special instance methods of a python object:
   http://docs.python.org/2/reference/datamodel.html#special-method-names

Changes
-------

A short sketch of the changes done in each release.

Release 0.1.4
~~~~~~~~~~~~~

The following was fixed in Release 0.1.4:

  * Fixed an issue with variadic methods. Sometimes definitions
    of variadic methods added after the method was already called
    where not added.
  * Specified and implemented a precedence rule for overlapping
    variadic methods of generic functions.
  * Improved generated documentation for variadic methods.
  * Fixed the markup of some notes in the documentation.

Release 0.1.3
~~~~~~~~~~~~~

The following was changed in Release 0.1.3:

  * Added variadic methods, e.g. multi-methods with a
    variable number of arguments.
  * Improved the long description text a bit
    and fixed bug in its markup.
  * Fixed invalid references in the long description.

Release 0.1.2
~~~~~~~~~~~~~

The following was changed in Release 0.1.2:

  * Added a generic functions for :meth:`gf.Object.__call__`.
  * Added a :class:`gf.go.FinalizingMixin`.
  * :func:`gf.generic` now also accepts a type.
  * Improved the exception information for ambiguous calls.
  * Fixed some documentation glitches.

Release 0.1.1
~~~~~~~~~~~~~

This was the initial release.

