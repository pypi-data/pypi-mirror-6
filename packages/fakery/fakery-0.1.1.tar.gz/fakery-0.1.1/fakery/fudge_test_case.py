import fudge
from unittest import TestCase
from fudge.util import wraps

class FudgeTestCase(TestCase):

    did_patch_methods = False
    patches = []

    def patch_attribute(self, module_name, object_name):
        object_mock = fudge.Fake(object_name).is_a_stub()
        object_patch = fudge.patch_object(module_name, object_name, object_mock)
        FudgeTestCase.patches.append(object_patch)
        return object_mock

    def patch_method(self, module_name, method_name):
        method_mock = fudge.Fake(method_name).is_callable()
        method_patch = fudge.patch_object(module_name, method_name, method_mock)
        FudgeTestCase.patches.append(method_patch)
        return method_mock

    def patch_constructor(self, module_name, class_name):
        type_mock = fudge.Fake(class_name)
        type_patch = fudge.patch_object(module_name, class_name, type_mock)
        FudgeTestCase.patches.append(type_patch)
        return type_mock.is_callable().returns_fake().is_a_stub()

    def restore_patches(self):
        for patch in FudgeTestCase.patches:
            patch.restore()
        FudgeTestCase.patches = []

    def __init__(self, name):
        if not self.__class__.did_patch_methods:
            self.__class__.did_patch_methods = True
            self._fudgify_methods()

        super(FudgeTestCase, self).__init__(name)

    def _fudgify_methods(self):
        tear_down = None

        for key in self.__class__.__dict__:
            if key.startswith("test"):
                item = self.__class__.__dict__[key]
                setattr(self.__class__, key, self.with_fakes(item))
            if key.startswith("tearDown"):
                tear_down = self.__class__.__dict__[key]

        if not tear_down:
            tear_down = lambda self: super(self.__class__, self).tearDown()

        setattr(self.__class__, "tearDown", self.clear_expectations(tear_down))

    def with_fakes(self, method):
        @wraps(method)
        def apply_with_fakes(*args, **kw):
            fudge.clear_calls()
            method(*args, **kw)
            fudge.verify()
        return apply_with_fakes

    def clear_expectations(self, method):
        @wraps(method)
        def apply_clear_expectations(*args, **kw):
            fudge.clear_expectations()
            self.restore_patches()
            method(*args, **kw)
        return apply_clear_expectations
