Application Programming Interface
=================================
The generic function package provides means to define generic functions
and multi-methods. Additionally classes are provided that enable the
user to implement nearly all of Python's special methods as multi-methods.

.. module:: gf
   :synopsis: Provides generic functions, multi-methods and convenience classes
   

Basic Usage
-----------
One can define generic functions are generics and multi-methods with
Python`s special method support with juts two decorator functions and
optionally one decorator method.

Defining Generic Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~
Generic functions must be defined with the :func:`generic`-function.

.. decorator:: generic(default_function)

    Create a generic function with a default implementation provided
    by `default_function`.

    :param callable_object default_function: The generic's default implementation.

    The generic's name and docstring are taken from the `default_function`.
    
    Specialisations for different call signatures can be added with the
    :func:`method` and :meth:`<generic>.method` decorators.

    .. note:: `callable_object` can be a function or a type (a new style class).

    For example the generic :func:`foo`'s default implemenations just
    answers the arguments passed as a tuple:

        >>> from gf import generic
        >>> @generic
        ... def foo(*arguments):
        ...     """Answers its arguments."""
        ...     return arguments

    :func:`foo` can be called just like an ordinary function.

        >>> foo(1, 2, 3)
        (1, 2, 3)


.. function:: generic()

    Create an unnamed generic function with no default function and no implementation.

    Defining a generic function in this way has the same effect as defining a
    generic function with a default function that raised a `NotImplementedError`.

    This form is the simplest way to define a generic:

        >>> bar = generic()

    If this generic function is called a `NotImplementedError`  is raised:

    >>> bar("Hello", U"World")
    Traceback (most recent call last):
    ...
    NotImplementedError: Generic None has no implementation for type(s): __builtin__.str, __builtin__.unicode

    .. note:: The name is added later when the first multi-method is added
           with :func:`method`.


.. function:: generic(name)

    Create a generic function with a name and no default implementation.

    :param basestring name: The generic's name assessable with
                            the `.__name__` attribute.

    If you define :func:`bar`in this may the `NotImplementedError`
    raised will contain the generics name:
 
        >>> bar = generic("bar")
        >>> bar("Hello", U"World")
        Traceback (most recent call last):
        ...
        NotImplementedError: Generic 'bar' has no implementation for type(s): __builtin__.str, __builtin__.unicode

    The docstring however is still `None`:

        >>> print bar.__doc__
        None

.. function:: generic(name, doc)

    Create a generic function with a name and a docstring, but 
    no default implementation.

    :param basestring name: The generic's name accessible with
                           the `.__name__` attribute.
    :param basestring doc: The generic's docstring accessible with
                           the `.__doc__` attribute.


        >>> bar = generic("bar", "A silly generic function for demonstration purposes")

    The generic now also has a docstring:

        >>> print bar.__doc__
        A silly generic function for demonstration purposes

Adding Multi-Methods
~~~~~~~~~~~~~~~~~~~~
Multi-methods can be added to a generic function with the :func:`method`-function
or the :meth:`<generic>.method` method.

.. decorator:: method(*types)(implementation_function)

    Add a multi-method for the types given to the generic decorated.

    :param type types: An optionally empty list of built-in types or
                       new-style classes.
    :param FunctionType implementation_function: The function implementing
        the multi-method.

    A multi-method specialising the :func:`foo` generic for
    two integers can be added as such:

        >>> from gf import method
        >>> @method(int, int)
        ... def foo(i0, i1):
        ...     return i0 + i1

    This makes :func:`foo` answer 3 for the following call:

        >>> foo(1, 2)
        3

    .. caution:: The generic function the multi-method is added to, must be defined
           in the multi-method's implementation function's global name-space.

           If this is not the case use the :meth:`<generic>.method`
           decorator.

.. decorator:: variadic_method(*types)(implementation_function)

    Add a multi-method with a variable number of arguments to
    the generic decorated.

    :param type types: An optionally empty list of built-in types or
                       new-style classes.
    :param FunctionType implementation_function: The function implementing
        the multi-method.

    This does essentially the same as :func:`method`, but
    accepts additional arguments to ones the specified by types.
    This is done by virtually adding an infinite set of of method
    defintions with the type :class:`object` used for the
    unspecified types. 

    This decorator can be used to implement functions like this:

    .. code:: python

        @variadic_method(TC)
        def varfun1(tc, *arguments):
            return (tc,) + tuple(reversed(arguments))

    This function can be called like this:

    .. code:: python

        varfun1(to, "a", "b", "c")

    and behaves in this case like being defined as:
    
    .. code:: python

        @method(TC, object, object, object)
        def varfun1(tc, *arguments):
            return (tc,) + tuple(reversed(arguments))

    Overlaps of variadic method definitions are always resolved
    toward the method with more specified types being selected.

    This means, that this this function:

    .. code:: python

        @variadic_method(object)
        def foo(*arguments):
            return arguments

    is always perferred over that function:

    .. code:: python

        @variadic_method()
        def foo(*arguments):
            return list(reversed(arguments))

    when called like:

    .. code:: python

        foo("Sepp")

.. decorator:: <generic>.method(*types)(implementation_function)

    Directly define a multi-method for the types given to `<generic>`.
    
    :param type types: An optionally empty list of built-in types or
                       new-style classes.
    :param FunctionType implementation_function: The function implementing
        the multi-method.

    `<generic>` needs not to be available in the implementation
    function's name-space. Additionally `implementation_function`
    can have a different name than the generic. The later leads
    to defining an alias of the generic function.

    For example a multi-method also available as bar can be defined as such:

        >>> @foo.method(str)
        ... def foobar(a_string):
        ...     return "<%s>" % a_string

    With this definition one can either call :func:`foo` with a string
    as follows:

        >>> foo("Hi")
        '<Hi>'

    Or :func:`foobar`:

        >>> foobar("Hi")
        '<Hi>'

.. decorator:: <generic>.variadic_method(*types)(implementation_function)

    Directly define a multi-method with a variable number of arguments
    for the types given to `<generic>`.
    
    :param type types: An optionally empty list of built-in types or
                       new-style classes.
    :param FunctionType implementation_function: The function implementing
        the multi-method.

    This decorator is the variadic variant of :func:`<generic>.method`.


Calling Other Multi-Methods of The Same Generic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
As it is sometimes necessary with ordinary single dispatch methods
to call methods defined in a base class, it it is sometimes
necessary to reuse other implementations of a generic.
For this purpose the generic has :meth:`super`-method.

.. method:: <generic>.super(*types)(*arguments)

    :param type types: An optionally empty list of built-in types or
                       new-style classes.
    :param arguments: An optionally empty list of Python objects.

    Directly retrieve and call the multi-method that implements
    the generic's functionally for `types`.

    One can add a (silly) implementation for unicode objects
    to :meth:`foo` like this:

        >>> @method(unicode)
        ... def foo(a_string):
        ...     return foo.super(object)(a_string)

    With this definition the generic's default implementation
    will be called for unicode-objects:

        >>> foo(U"Sepp")
        (u'Sepp',)

    While calling :func:`foo` wthit a string still yields
    the old result:

        >>> foo("Sepp")
        '<Sepp>'

    .. caution:: It is not checked whether the `arguments` passed
           are actually instances of `types`. This is consistent
           with Python's notion of duck typing.


Advanced Usage
--------------

The :mod:`gf`-package also provides an abstract base class called
:class:`gf.AbstractObject` and class called :class:`gf.Object`. 

Both classes map nearly all of Python's special methods to generic
functions.

There is also a :class:`Writer`-class and some convenience
and helper generics like :func:`as_string`, :func:`spy`,
:func:`__out__` and :func:`__spy__`.

The implementation of the aforementioned objects is contained
in the :mod:`gf.go`, but the objects are also available
for direct import from :mod:`gf`.

The following text is generated from the docstring in :mod:`gf.go`.

.. automodule:: gf.go
    :members:
    :special-members:
