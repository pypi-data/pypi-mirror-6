import inspect
import unittest

import mock

import fluenttest


class FluentTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.class_attrs = dict(
            (a.name, a)
            for a in inspect.classify_class_attrs(fluenttest.TestCase)
        )

    def should_implement_setup_class(self):
        self.assert_is_class_method('setup_class')

    def should_implement_teardown_class(self):
        self.assert_is_class_method('teardown_class')

    def should_implement_arrange(self):
        self.assert_is_class_method('arrange')

    def should_implement_act(self):
        self.assert_is_class_method('act')

    def should_implement_destroy(self):
        self.assert_is_class_method('destroy')

    def should_be_a_new_class(self):
        class _NewStyleClass(object):
            pass
        self.assertIsInstance(fluenttest.TestCase, type(_NewStyleClass))

    def assert_is_class_method(self, name):
        self.assertEquals(self.class_attrs[name].kind, 'class method')


class PatchedFluentTestCase(unittest.TestCase):
    allowed_exceptions = ()

    @classmethod
    def setUpClass(cls):
        super(PatchedFluentTestCase, cls).setUpClass()
        cls._active_patches = []
        cls.patches = {}
        for name, patch in cls.make_patches().items():
            cls.patches[name] = patch.start()
            cls._active_patches.append(patch)

    @classmethod
    def make_patches(cls):
        return {
            'allowed_exceptions': mock.patch.object(
                fluenttest.test_case.TestCase,
                'allowed_exceptions',
                cls.allowed_exceptions,
            ),
            'act': mock.patch('fluenttest.test_case.TestCase.act'),
        }

    @classmethod
    def tearDownClass(cls):
        for patch in cls._active_patches:
            patch.stop()
        super(PatchedFluentTestCase, cls).tearDownClass()


class SetupClass(PatchedFluentTestCase):

    @classmethod
    def setUpClass(cls):
        super(SetupClass, cls).setUpClass()

        cls.test = fluenttest.TestCase()
        cls.test.setup_class()

    def should_call_act(self):
        self.patches['act'].assert_called_once_with()

    def should_create_and_initialize_exception_attribute(self):
        self.assertIsNone(self.test.exception)

    def should_create_and_initialize_allowed_exceptions_attribute(self):
        self.assertEquals(self.test.allowed_exceptions, ())


class SetupClassWithArrange(SetupClass):

    @classmethod
    def make_patches(cls):
        patch_dict = super(SetupClassWithArrange, cls).make_patches()
        patch_dict['arrange'] = mock.patch(
            'fluenttest.test_case.TestCase.arrange')
        return patch_dict

    def should_call_arrange(self):
        self.test.arrange.assert_called_once_with()


class SetupClassWithDestroy(SetupClass):

    @classmethod
    def make_patches(cls):
        patch_dict = super(SetupClassWithDestroy, cls).make_patches()
        patch_dict['destroy'] = mock.patch(
            'fluenttest.test_case.TestCase.destroy')
        return patch_dict

    def should_call_destroy(self):
        self.test.destroy.assert_called_once_with()


class _PatchedBaseTest(PatchedFluentTestCase):

    @classmethod
    def setUpClass(cls):
        super(_PatchedBaseTest, cls).setUpClass()
        with mock.patch('fluenttest.test_case.mock') as cls.mock_module:
            cls.patcher = cls.mock_module.patch.return_value
            cls.test = fluenttest.TestCase()
            cls.test.setup_class()
            try:
                cls.execute_test_steps()
            except Exception as exc:
                cls.captured_exception = exc
            finally:
                cls.test.teardown_class()


class TeardownClass(_PatchedBaseTest):

    @classmethod
    def execute_test_steps(cls):
        cls.patches = [mock.Mock(), mock.Mock()]
        cls.mock_module.patch.side_effect = cls.patches

        cls.test.patch('first_patch')
        cls.test.patch('second_patch')

    def should_stop_all_patches(self):
        for patcher in self.patches:
            patcher.stop.assert_called_once_with()


class WhenTearingDownWithFailedPatch(_PatchedBaseTest):

    @classmethod
    def execute_test_steps(cls):
        cls.good_patch = mock.Mock()
        # patch().start() fails when patching something that doesn't exist.
        cls.bad_patch = mock.Mock()
        cls.bad_patch.start.side_effect = AttributeError
        cls.mock_module.patch.side_effect = [
            cls.good_patch,
            cls.bad_patch,
        ]

        cls.test.patch('working_patch')
        cls.test.patch('failing_patch')

    def should_stop_working_patch(self):
        self.good_patch.stop.assert_called_once_with()

    def should_not_stop_failed_patch(self):
        self.assertFalse(self.bad_patch.stop.called)


class WhenPatchingFails(_PatchedBaseTest):

    @classmethod
    def execute_test_steps(cls):
        cls.expected_exception = Exception()
        cls.patcher.start.side_effect = cls.expected_exception

        cls.test.patch('patch_target')

    def should_propagate_exception(self):
        self.assertIs(self.captured_exception, self.expected_exception)


class WhenPatchingAnInstance(_PatchedBaseTest):

    patch_target = 'target.class'
    kwargs = {'kwarg': mock.sentinel.kwarg}

    @classmethod
    def execute_test_steps(cls):
        cls.patched_class = cls.patcher.start.return_value
        cls.return_value = cls.test.patch_instance(
            'target.class', **cls.kwargs)

    def should_return_patched_class_and_new_instance(self):
        self.assertEquals(
            self.return_value,
            (self.patched_class, self.patched_class.return_value),
        )

    def should_call_patch(self):
        self.mock_module.patch.assert_called_once_with(
            self.patch_target, **self.kwargs)


class TheDefaultActImplementation(unittest.TestCase):

    def should_raise_NotImplementedError(self):
        with self.assertRaises(NotImplementedError):
            fluenttest.TestCase.act()


class RunTestWithException(PatchedFluentTestCase):

    @classmethod
    def setUpClass(cls):
        super(RunTestWithException, cls).setUpClass()

        cls.raised_exception = LookupError()
        cls.patches['act'].side_effect = cls.raised_exception

        cls.test = fluenttest.TestCase()
        try:
            cls.test.setup_class()
        except Exception as exc:
            cls.caught_exception = exc

    @classmethod
    def make_patches(cls):
        patch_dict = super(RunTestWithException, cls).make_patches()
        patch_dict['destroy'] = mock.patch(
            'fluenttest.test_case.TestCase.destroy')
        return patch_dict

    def should_call_destroy(self):
        self.test.destroy.assert_called_once_with()


class WhenRunTestRaisesAnAllowedException(RunTestWithException):
    allowed_exceptions = LookupError

    def it_should_be_captured(self):
        self.assertIs(self.test.exception, self.raised_exception)


class WhenRunTestRaisesUnexpectedException(RunTestWithException):
    allowed_exceptions = KeyError

    def it_should_be_propagated(self):
        self.assertIs(self.caught_exception, self.raised_exception)
