#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2015 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.utils.path import getpath
from b3j0f.rcm.controller.core import Controller
from b3j0f.rcm.controller.impl import (
    ImplController,
    ImplAnnotation,
    B2CAnnotation, C2BAnnotation, C2B2CAnnotation
)


class BaseImplControllerTest(UTCase):

    def setUp(self):

        self.controller = ImplController()
        Controller.bind_all(self.controller, self.controller)


class ImplControllerTest(BaseImplControllerTest):
    """Test impl controller.
    """

    def test_cls_str(self):
        """Test cls property with a name.
        """

        self.controller.cls = getpath(ImplControllerTest)
        self.assertIs(self.controller.cls, ImplControllerTest)

    def test_cls_cls(self):
        """Test cls property with cls.
        """

        self.controller.cls = ImplControllerTest
        self.assertIs(self.controller.cls, ImplControllerTest)

    def test_cls_none(self):
        """Test to Nonify cls property.
        """

        self.test_cls_cls()

        self.controller.cls = None
        self.assertIsNone(self.controller.cls)

    def test_impl(self):
        """Test impl with impl annotation.
        """

        impl = object()

        self.controller.impl = impl
        self.assertIs(self.controller.impl, impl)
        self.assertIs(self.controller.impl.__class__, object)

    def test_impl_none(self):
        """Test to nonify an impl.
        """

        self.test_impl()

        self.controller.impl = None
        self.assertIs(self.controller.impl, None)
        self.assertIs(self.controller.cls, None)

    def test_instantiate(self):
        """Test to update the controller.
        """

        class TestImpl(object):

            def __init__(self, a, b=1):

                self.a = a
                self.b = b

        self.controller.cls = TestImpl

        self.assertRaises(
            ImplController.ImplError, self.controller.instantiate
        )

        new_impl = self.controller.instantiate(kwargs={'a': 0})
        self.assertEqual(new_impl.a, 0)
        self.assertEqual(new_impl.b, 1)

    def test_get_resource_stateful(self):
        """Test to get a resource with stateful.
        """

        self.controller.stateful = True

        self.controller.cls = object

        res0 = self.controller.get_resource()
        res1 = self.controller.get_resource()

        self.assertIs(res0, res1)

    def test_get_resource_stateless(self):
        """Test to get a resource with stateful.
        """

        self.controller.stateful = False

        self.controller.cls = object

        res0 = self.controller.get_resource()
        res1 = self.controller.get_resource()

        self.assertIsNot(res0, res1)


class TestImplAnnotation(BaseImplControllerTest):
    """Test ImplAnnotation.
    """

    class TestImplAnnotation(ImplAnnotation):

        def __init__(self, implcontrollertest, *args, **kwargs):

            super(TestImplAnnotation.TestImplAnnotation, self).__init__(
                *args, **kwargs
            )

            self.implcontrollertest = implcontrollertest

        def apply(self, *args, **kwargs):

            self.implcontrollertest.count += 1

        def unapply(self, *args, **kwargs):

            self.implcontrollertest.count -= 1

    def setUp(self):

        super(TestImplAnnotation, self).setUp()

        self.count = 0

    def test_apply(self):
        """Test apply method.
        """

        cls = str

        self.impl = cls()

        annotation = TestImplAnnotation.TestImplAnnotation(self)
        annotation(cls)
        annotation(cls.__format__, ctx=cls)

        annotation.apply(
            component=None, impl=self.impl
        )
        annotation.apply(
            component=None, impl=self.impl, member=cls.__format__
        )
        self.assertEqual(self.count, 2)

        return annotation

    def test_unapply(self):
        """Test unapply method.
        """

        annotation = self.test_apply()

        annotation.unapply(
            component=None,
            impl=self.impl
        )
        annotation.unapply(
            component=None,
            impl=self.impl,
            member=self.impl.__format__
        )
        self.assertEqual(self.count, 0)

    def test_apply_on(self):
        """Test apply_on method.
        """

        cls = str

        self.impl = cls()

        annotation = TestImplAnnotation.TestImplAnnotation(self)
        annotation(cls)
        annotation(cls.__format__, ctx=cls)

        ImplAnnotation.apply_on(
            component=None, impl=self.impl
        )
        self.assertEqual(self.count, 2)

    def test_unapply_from(self):
        """Test unapply_from method.
        """

        self.test_apply_on()

        ImplAnnotation.unapply_from(
            component=None,
            impl=self.impl
        )
        self.assertEqual(self.count, 0)

    def test_impl(self):
        """Test impl with impl annotation.
        """

        cls = str

        impl = cls()

        annotation = TestImplAnnotation.TestImplAnnotation(self)
        annotation(cls)
        annotation(cls.__format__, ctx=cls)

        self.controller.impl = impl
        self.assertIs(self.controller.impl, impl)
        self.assertIs(self.controller.impl.__class__, cls)
        self.assertEqual(self.count, 2)

    def test_impl_none(self):
        """Test to nonify an impl.
        """

        self.test_impl()

        self.controller.impl = None
        self.assertIs(self.controller.impl, None)
        self.assertIs(self.controller.cls, None)
        self.assertEqual(self.count, 0)

    def test_instantiate(self):
        """Test to update the controller.
        """

        @TestImplAnnotation.TestImplAnnotation(self)
        class TestImpl(object):

            @TestImplAnnotation.TestImplAnnotation(self)
            def __init__(self, a, b=1):

                self.a = a
                self.b = b

            @TestImplAnnotation.TestImplAnnotation(self)
            def __call__(self):

                pass

        self.controller.cls = TestImpl

        self.assertRaises(
            ImplController.ImplError, self.controller.instantiate
        )

        new_impl = self.controller.instantiate(kwargs={'a': 0})
        self.assertEqual(new_impl.a, 0)
        self.assertEqual(new_impl.b, 1)
        self.assertEqual(self.count, 3)


class TestB2CAnnotation(BaseImplControllerTest):
    """Test B2CAnnotation.
    """

    def setUp(self, *args, **kwargs):

        super(TestB2CAnnotation, self).setUp(*args, **kwargs)

        self.count = 0

    class Ann(B2CAnnotation):

        def get_result(self, result, **kwargs):

            result.count += 1

    def test_get_result(self):
        """Test get_result method.
        """

        annotation = TestB2CAnnotation.Ann()

        annotation.get_result(result=self)
        self.assertEqual(self.count, 1)

    def test_call_getter(self):
        """Test call_getter method.
        """

        class Test(object):

            def __init__(self, tb2ca=self):

                self.tb2ca = tb2ca

            @TestB2CAnnotation.Ann()
            def test(self):
                return self.tb2ca

        test = Test()
        B2CAnnotation.call_getter(
            component=None, impl=test, getter=test.test
        )
        self.assertEqual(self.count, 1)

    def test_call_getters(self):
        """Test call_getters method.
        """

        class Test(object):

            def __init__(self, tb2ca=self):

                self.tb2ca = tb2ca

            @TestB2CAnnotation.Ann()
            def test(self):
                return self.tb2ca

        test = Test()
        B2CAnnotation.call_getters(
            component=None, impl=test
        )
        self.assertEqual(self.count, 1)


class TestC2BAnnotation(BaseImplControllerTest):
    """Test C2BAnnotation.
    """

    class Ann(C2BAnnotation):

        def __init__(self, test, *args, **kwargs):

            super(TestC2BAnnotation.Ann, self).__init__(*args, **kwargs)

            self.test = test

        def get_value(self, *args, **kwargs):

            return self.test

    def test_constructor_empty(self):
        """Test to inject a parameter in an empty constructor.
        """

        class Test(object):

            @TestC2BAnnotation.Ann(self)
            def __init__(self):
                pass

        self.assertRaises(
            C2BAnnotation.C2BError,
            C2BAnnotation.call_setter,
            component=None,
            impl=Test
        )

    def test_constructor(self):
        """Test to inject a parameter in a cls.
        """

        class Test(object):

            @TestC2BAnnotation.Ann(self)
            def __init__(self, test):

                self.test = test

        impl = C2BAnnotation.call_setter(component=None, impl=Test)

        self.assertIs(impl.test, self)

    def test_constructor_name(self):
        """Test to inject a parameter in a cls with a dedicated name.
        """

        class Test(object):

            @TestC2BAnnotation.Ann(self, param='test')
            def __init__(self, a=2, b=1, test=None):

                self.test = test

        impl = C2BAnnotation.call_setter(component=None, impl=Test)

        self.assertIs(impl.test, self)

    def test_routine_empty(self):
        """Test to inject a parameter in an empty routine.
        """

        class Test(object):

            @TestC2BAnnotation.Ann(self)
            def test(self):
                pass

        test = Test()

        self.assertRaises(
            C2BAnnotation.C2BError,
            C2BAnnotation.call_setter,
            component=None,
            impl=test,
            setter=test.test
        )

    def test_routine(self):
        """Test to inject a parameter in a routine.
        """

        class Test(object):

            @TestC2BAnnotation.Ann(self)
            def test(self, test):
                self.test = test

        test = Test()

        C2BAnnotation.call_setter(
            component=None, impl=test, setter=test.test
        )
        self.assertIs(test.test, self)

    def test_routine_param(self):
        """Test to inject a parameter in a routine.
        """

        class Test(object):

            @TestC2BAnnotation.Ann(self, param='test')
            def test(self, a=0, b=1, test=None):
                self.test = test

        test = Test()

        C2BAnnotation.call_setter(
            component=None, impl=test, setter=test.test
        )
        self.assertIs(test.test, self)


class TestC2B2CAnnotation(BaseImplControllerTest):
    """Test C2B2CAnnotation.
    """

    class C2B2C(C2B2CAnnotation):

        def __init__(self, tcbc, *args, **kwargs):

            super(TestC2B2CAnnotation.C2B2C, self).__init__(*args, **kwargs)

            self.tcbc = tcbc

        def get_value(self, *args, **kwargs):

            self.tcbc.count_value += 1

            return self.tcbc

        def get_result(self, result, *args, **kwargs):

            result.count_result += 1

    def setUp(self, *args, **kwargs):

        super(TestC2B2CAnnotation, self).setUp(*args, **kwargs)

        self.count_value = 0
        self.count_result = 0

    def test_routine(self):

        class Test(object):

            @TestC2B2CAnnotation.C2B2C(self, param='test')
            def test(self, a=0, test=None):
                self._test = test
                return test

        test = Test()

        C2BAnnotation.call_setters(
            component=None, impl=test, call_getters=True
        )
        self.assertEqual(self.count_value, 1)
        self.assertEqual(self.count_result, 1)
        self.assertIs(test._test, self)

if __name__ == '__main__':
    main()
