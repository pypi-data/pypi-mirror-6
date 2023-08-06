from fluenttest.class_based import ClassTester, lookup_class, the_class
from fluenttest.test_case import TestCase

version_info = (2, 0, 0)
__version__ = '.'.join(str(x) for x in version_info)
__all__ = [
    'ClassTester',
    'TestCase',
    'lookup_class',
    'the_class',
    '__version__',
    'version_info',
]
