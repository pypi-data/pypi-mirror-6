.. py:currentmodule:: fluenttest

Unit Testing
============

:py:class:`TestCase` follows the *Arrange, Act, Assert* pattern
espoused by the TDD community; however, the implementation may seem
confounding at first. The arrange and action steps are implemented as class
methods and the assertions are implemented as instance methods.  This is a
side-effect of using existing test runners and little more.  The goal is to
assure that the arrangement and action methods are run precisely once before
the assertions are checked.  The common unit test running tools follow the
same approach as their xUnit brethren.

    #. Run class-level *setup* method(s)
    #. For each test case defined in the class, do the following:
        #. Run the instance-level *setup* methods(s)
        #. Run the test function
        #. Run the instance-level *tear down* method(s)
    #. Run class-level *tear down* methods

The AAA approach to unit testing encourages a single action under test
along with many atomic assertions.  In an xUnit framework, it is natural to
model assertions as specific tests.  Each test should be a single assertion
to ensure that the root of a failure is as succinct as possible.  Since we
want many small assertions for a single arrangement or environment, we use
the class-level setup and tear down methods.

:py:class:`TestCase` implements a class-level setup method that
delegates the *arrange* and *action* steps to sub-class defined methods named
``arrange`` and ``act``.  Test case implementations should implement class
methods named ``arrange`` and ``act`` then implement test cases for each
assertion::

    class TheFrobinator(TestCase):
        @classmethod
        def arrange(cls):
            super(TheFrobinator, cls).arrange()
            cls.swizzle = cls.patch('frobination.internal.swizzle')
            cls.argument = 'One'
            cls.frobinator = Frobinator()

        @classmethod
        def act(cls):
            cls.return_value = cls.frobinator.frobinate(cls.argument)

        def test_should_return_True(self):
            assert self.return_value == True

        def test_should_swizzle_the_argument(self):
            self.swizzle.assert_called_once_with(self.argument)


Patching
--------

The example included an instance of creating a patch as well.  Fluent Test
incorporates Michael Foord's excellent `mock`_ library and exposes patching
as the :py:meth:`TestCase.patch` and :py:meth:`TestCase.patch_instance`
methods.  Both methods patch out a specific target from the time that the
patch method is called until the class-level tear down method is invoked.
Patching is a great method for isolating the class that is under test since
you can replace the collaborating classes, control their behavior, and place
assertions over each of the interactions.

There are two primary use cases that :py:class:`TestCase` exposes.  The most
common one is exposed by :py:meth:`TestCase.patch`.  It patches the target by
calling :py:func:`mock.patch`, `starts the patch`_, and returns the patched
object.  :py:meth:`TestCase.patch_instance` is similar except that it is really
meant for patching types.  It returns a tuple of the patcher and
``patcher.return_value``.  This simplifies the common case of patching a class
to control/inspect the instance of the class created in the unit under test.
To continue our previous example, if the ``Frobinator`` creates an instance
of the ``Swizzler``, then we can use the following to test it::

    class TheFrobinator(TestCase):
        @classmethod
        def arrange(cls);
            super(TheFrobinator, cls).arrange()
            cls.swizzler_cls, cls.swizzler_inst = cls.patch_instance(
                'frobination.Swizzler')
            cls.argument = 'One'
            cls.frobinator = Frobinator()

        @classmethod
        def act(cls):
            cls.return_value = cls.frobinator.frobinate(cls.argument)

        def test_should_create_a_Swizzler(self):
            self.swizzler_cls.assert_called_once_with()

        def test_should_swizzle_the_arguments(self):
            self.swizzler_inst.swizzle.assert_called_once_with(self.argument)


Exception Handling
------------------

Another useful extension that :py:class:`TestCase` provides is to wrap the
action in a ``try``-``except`` block.  The test case can list exceptions that
it is interested in receiving by adding the class attribute
:py:attr:`~TestCase.allowed_exceptions` containing a ``tuple`` of exception
classes.  When an exception is raised from :py:meth:`~TestCase.act` and it is
listed in ``allowed_exceptions``, then it is saved in the
:py:attr:`~TestCase.exception` for later inspection.  Otherwise, it is raised
and propagates outward.


.. _mock: https://mock.readthedocs.org/en/latest/
.. _starts the patch: https://mock.readthedocs.org/en/latest/patch.html#patch-methods-start-and-stop
