"""Tests for the generic object (`go`) module."""

import sys, os
sys.path.insert(0,
        os.path.abspath(
            os.path.normpath(
                os.path.join(
                    os.path.basename(sys.argv[0]), os.pardir))))
del os, sys

from unittest import TestCase as BaseTestCase
from gf import (Object, FinalizingMixin, Writer,
        generic, method, variadic_method,
        __init__, __call__, __del__,
        __spy__, __add__, __out__, as_string, spy,
        __eq__, __ne__,
        )



class TestCase(BaseTestCase):
    """The base class of all the tests."""

    def setUp(self):
        """Set up the test class."""

        class TC(Object):
            """A simple test class."""

        @method(TC)
        def __init__(test_object):
            test_object.a0 = "v0"
            test_object.a1 = "v1"
        
        self.TC = TC


class InitTestCase(TestCase):
    """Test the initialisation."""


    def test_init(self):
        """Test the initialisation of our test class."""
        to = self.TC()
        self.failUnlessEqual(to.a0, "v0")
        self.failUnlessEqual(to.a1, "v1")
        self.failUnless(".TC object at" in str(to))


class OutputTestCase(TestCase):
    """Test the output and string conversion functions."""

    def setUp(self):
        """Setup additional output methods."""
        super(OutputTestCase, self).setUp()
        TC = self.TC

        @method(TC, Writer)
        def __out__(test_object, write):
            write("TC(%s, %s)", test_object.a0, test_object.a1)

        @method(TC, Writer)
        def __spy__(self, write):
            __spy__.super(Object, Writer)(self, write)
            write("(")
            __spy__(self.a0, write)
            write(", ")
            __spy__(self.a1, write)
            write(")")

    def test_string_conversion(self):
        """Test the string conversion functions."""
        to = self.TC()
        object_as_string = str(to)
        self.failUnlessEqual(object_as_string, "TC(v0, v1)")
        self.failUnlessEqual(object_as_string, as_string(to))
        debug_string = repr(to)
        self.failUnless(".TC object at" in debug_string)
        self.failUnless(debug_string.endswith(">('v0', 'v1')"))
        self.failUnlessEqual(debug_string, spy(to))


class OperatorTestCase(TestCase):
    """Test a bit of the operators."""

    def setUp(self):
        """Setup additional output methods."""
        super(OperatorTestCase, self).setUp()
        TC = self.TC

        @method(TC, int)
        def __add__(self, an_integer):
            return self.a0 * self.a1 + an_integer

        @method(TC, int)
        def __call__(self, an_integer):
            return "%r %r %d" % (self.a0, self.a1, an_integer)

    def test_add(self):
        """Test the newly defined addition method.""" 
        to = self.TC()
        to.a0 = 2
        to.a1 = 3
        self.failUnlessEqual(to + 3, 9)
        self.failUnlessRaises(NotImplementedError, lambda: 3 + to) 

    def test_call(self):
        """Test calling the instance."""
        to = self.TC()
        self.failUnlessEqual("'v0' 'v1' 11", to(11))


class FinalizingTestCase(TestCase):
    """Test the finalizing functionality."""

    def setUp(self):
        """Set up an additional subclass."""
        super(FinalizingTestCase, self).setUp()
        self.fo = None

        class FC(FinalizingMixin, self.TC):
            """A test class with a `__del__`genric implementation."""
        
        @method(FinalizingMixin)
        def __del__(an_fo):
            self.fo = an_fo

        self.FC = FC

    def test_finalisation(self):
        """Test an object's finalisation."""
        self.failUnless(self.fo is None)
        fo = self.FC()
        self.failUnless(self.fo is None)
        del fo
        self.failIf(self.fo is None)


class VariadicTestCase(TestCase):
    """Test variadic methods."""
    
    def test_variadic(self):
        """Test variadic methods."""

        varfun0 = generic()
        varfun1 = generic()

        @varfun0.variadic_method()
        def varfun0(*arguments):
            return tuple(reversed(arguments))
        
        @varfun1.variadic_method(self.TC)
        def varfun1(tc, *arguments):
            return (tc,) + tuple(reversed(arguments))
        
        @method(self.TC, self.TC)
        def __eq__(tc0, tc1):  # Make `failUnlessEqual`work!
            return tc0.a0 == tc1.a0 and tc0.a1 == tc1.a1
        
        @method(self.TC, tuple)
        def __eq__(tc0, t):  # Make `failUnlessEqual`work!
            return False
        
        @method(self.TC, self.TC)
        def __ne__(tc0, tc1):  # Make `failUnlessEqual`work!
            return tc0.a0 != tc1.a0 or tc0.a1 != tc1.a1

        self.failUnlessEqual(varfun0(1, 2, 3), (3, 2, 1))
        to = self.TC()
        self.failUnlessEqual(varfun1(to, "a", "b", "c"), (to, "c", "b", "a"))
        self.failUnlessRaises(NotImplementedError, varfun1, "Sepp")
        self.failUnlessEqual(varfun1(to), (to,))

        self.failUnlessEqual(varfun0(1, 2), (2, 1))

        @varfun0.method(int, int)
        def varfun0(one, two):
            return [one, two]

        self.failUnlessEqual(varfun0(1, 2), [1, 2])
        self.failUnlessEqual(varfun0(1, 2, 3), (3, 2, 1))
        self.failUnlessEqual(varfun0("1", "2"), ("2", "1"))

        varfun2 = generic()

        @varfun2.method(str, str)
        def varfun2(a, b):
            return "|".join((a, b))

        self.failUnlessEqual(varfun2("a", "b"), "a|b")

        @varfun2.variadic_method(str)
        def varfun2(a_string, *arguments):
            return "%s: %r" % (a_string, arguments)

        self.failUnlessEqual(varfun2("a", "b"), "a|b")
        self.failUnlessEqual(varfun2("c") , "c: ()")
        

    def test_override(self):
        """Test variadic overrides."""
        varfun0 = generic()

        @varfun0.variadic_method()
        def varfun0(*arguments):
            return None

        self.failUnlessEqual(varfun0("Test", "Test"), None)

        @varfun0.variadic_method(str)
        def varfun0(a_string, *arguments):
            return a_string

        self.failUnlessEqual(varfun0("Test", "Test"), "Test")

        varfun1 = generic()

        @varfun1.variadic_method(str)
        def varfun1(a_string, *arguments):
            return a_string

        self.failUnlessEqual(varfun1("Test", "Test"), "Test")

        @varfun1.variadic_method()
        def varfun1(*arguments):
            return None

        self.failUnlessEqual(varfun1("Test", "Test"), "Test")
        self.failUnlessEqual(varfun1(1, "Test"), None)
        self.failUnlessEqual(varfun1(1), None)


if __name__ == "__main__":
    from unittest import main
    main()
