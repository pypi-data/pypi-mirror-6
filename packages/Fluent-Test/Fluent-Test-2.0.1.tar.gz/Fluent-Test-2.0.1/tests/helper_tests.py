import unittest

from fluenttest import lookup_class


class LookupClass(unittest.TestCase):

    def should_return_class_when_given_class_as_argument(self):
        assert lookup_class(dict) is dict

    def should_import_class_by_absolute_path(self):
        assert lookup_class('unittest.TestCase') is unittest.TestCase

    def should_raise_AssertionError_when_given_something_else(self):
        assertion_caught = False
        try:
            lookup_class(1234)
        except AssertionError:
            assertion_caught = True
        assert assertion_caught
