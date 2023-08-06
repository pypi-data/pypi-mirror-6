"""Add useful utilities for class-based testing.

Classes
-------
- ``ClassTester`` - exposes assertions about a specific class

Functions
---------
- ``the_class`` - creates a ``ClassTester`` instance for a named class.
- ``lookup_class`` - finds a class by name.

"""
import inspect


class ClassTester:

    """Assert that a class matches certain conditions.

    :param type cls: the class under test

    This class provides a readable and efficient method for asserting
    that a class implements a particular interface.  Instead of
    specifying the interface using abstract base classes and the like,
    this test specifies the interface as a set of operations, parent
    classes, and class attributes.

    >>> probe = ClassTester(dict)
    >>> probe.implements_method('keys')
    True
    >>> probe.has_attribute('keys')
    True
    >>> probe.has_attribute('__class__')
    True

    Each assertion is implemented as a separate method that returns
    ``True`` or ``False``.  This is test runner agnostic so you can use
    the assertions with `nose <http://nose.readthedocs.org/>`_,
    :mod:`unittest`, or `py.test <http://pytest.org/>`_.

    """

    def __init__(self, cls):
        self.cls = cls
        self.info = {}
        for attr in inspect.classify_class_attrs(self.cls):
            self.info[attr.name] = attr

    def implements_method(self, name):
        """Does the class implement a method named *name*?"""
        return name in self.info and self.info[name].kind == 'method'

    def is_subclass_of(self, parent_class):
        """Is the class a subclass of *parent_class*?

        :param parent_class: a dotted class name or anything acceptable
            to :func:`.lookup_class`.

        """
        return issubclass(self.cls, lookup_class(parent_class))

    def has_attribute(self, name, typed=None, value=None):
        """Does the class have an attribute named *name*?

        :param str name: the name of the attribute to probe
        :param type typed: require the attribute to be an instance of
            this type
        :param value: require the attribute to have this specific value

        This method **does not** inspect the attributes of instances of
        the class.  It only examines the named attributes of the class
        itself.

        """
        if name not in self.info:
            return False
        if typed is not None:
            return isinstance(getattr(self.cls, name), typed)
        if value is not None:
            return getattr(self.cls, name) == value
        return True


def the_class(cls, matcher_class=None):
    """Return a :class:`~fluenttest.ClassTester` instance for ``cls``.

    :param cls: the ``class`` instance to inspect.
    :param type matcher_class: the type to instantiate, defaults
        to :class:`~fluenttest.ClassTester`

    """
    matcher_class = matcher_class or ClassTester
    return matcher_class(cls)


def lookup_class(target):
    """Find a class named ``target``.

    :param str target: the dot-separated name of the class to find,
        a ``class`` instance, or a ``type`` instance.
    :returns: a :class:`class` or :func:`type` instance

    """
    class NewStyle(object):
        pass

    class OldStyle:
        pass

    if isinstance(target, str):
        path = target.split('.')
        target = __import__(path[0])
        for next_segment in path[1:]:
            target = getattr(target, next_segment)
        return target
    if isinstance(target, (type(OldStyle), type(NewStyle))):
        return target
    raise AssertionError(
        "I can't look up a class name from {0}".format(target))
