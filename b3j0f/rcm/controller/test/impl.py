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
    B2CAnnotation, C2BAnnotation, C2B2CAnnotation, Ctrl2BAnnotation,
    Context, Port, Impl,
    getter_name, setter_name
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

    def test_get_value(self):
        """Test get_value method.
        """

        annotation = TestC2BAnnotation.Ann(self)

        value = annotation.get_value()
        self.assertIs(value, self)

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

    def test_call_setters(self):
        """Test call_setters method.
        """

        self.count = 0

        class Ann(C2BAnnotation):

            def __init__(self, test, *args, **kwargs):

                super(Ann, self).__init__(*args, **kwargs)

                self.test = test

            def get_value(self, *args, **kwargs):

                self.test.count += 1
                return self.test

        class Test(object):

            @Ann(self)
            def test0(self, a):
                pass

            @Ann(self)
            def test1(self, a):
                pass

            def test2(self, a):
                pass

        annotation = Ann(self)
        annotation(Test.test2)

        test = Test()

        C2BAnnotation.call_setters(component=None, impl=test)

        self.assertEqual(self.count, 3)

    def _get_parameterized_class(self):

        class Test(object):

            def __init__(self, *args, **kwargs):

                self.args = args
                self.kwargs = kwargs

        return Test

    def _get_class_w_ann(self, param=None, ispname=False, update=True):

        Test = self._get_parameterized_class()

        class TestAnn(C2BAnnotation):

            def get_value(
                self, component, pname=None, *args, **kwargs
            ):

                if pname is None:
                    pname = component

                result = pname

                return result

        annotation = TestAnn(param=param, ispname=ispname, update=update)
        annotation(
            Test.__init__, ctx=Test
        )

        return Test, annotation

    def test_force(self):
        """Test call_setter with in forcing.
        """

        Test = self._get_parameterized_class()

        impl = C2BAnnotation.call_setter(component=None, impl=Test, force=True)

        self.assertIsInstance(impl, Test)

    def _update_params(
        self, param=None, ispname=False, update=False,
        args=None, kwargs=None, **ks
    ):
        """Call C2BAnnotation._update_params with input parameters and return
        final args and kwargs.
        """

        if args is None:
            args = []

        if kwargs is None:
            kwargs = {}

        Test, ann = self._get_class_w_ann(
            param=param, ispname=ispname, update=update
        )

        ann._update_params(
            component=self, impl=Test, member=Test.__init__,
            args=args, kwargs=kwargs, **ks
        )

        return args, kwargs

    def test_not_force(self):
        """Test call_setter with not force.
        """

        Test = self._get_parameterized_class()

        impl = C2BAnnotation.call_setter(component=None, impl=Test)

        self.assertIsNone(impl)

    def test_update_params_none(self):
        """Test with param is None.
        """

        args, kwargs = self._update_params()

        self.assertEqual(args, [self])
        self.assertFalse(kwargs)

    def test_str_param(self):
        """Test with str param.
        """

        args, kwargs = self._update_params(
            param='test', kwargs={'test': 1}
        )

        self.assertFalse(args)
        self.assertEqual(kwargs, {'test': 1})

    def test_str_update_param(self):
        """Test to update existing str parameter.
        """

        args, kwargs = self._update_params(param='test', update=True)

        self.assertFalse(args)
        self.assertEqual(kwargs, {'test': self})

    def test_str_ispname_param(self):
        """Test param as a str and ispname.
        """

        param = 'test'
        args, kwargs = self._update_params(param=param, ispname=True)

        self.assertEqual(args, [param])
        self.assertFalse(kwargs)

    def test_list_param(self):
        """Test param as a list.
        """

        param = ['test', 'example', '']
        kwargs = {'test': None}
        args, kwargs = self._update_params(
            param=param, kwargs=kwargs
        )

        self.assertFalse(args)
        result = {'test': None, 'example': self, '': self}
        self.assertEqual(kwargs, result)

    def test_list_update_param(self):
        """Test param as a list.
        """

        param = ['test', 'example', '']
        kwargs = {'test': None}
        args, kwargs = self._update_params(
            param=param, kwargs=kwargs, update=True
        )

        self.assertFalse(args)
        result = {'test': self, 'example': self, '': self}
        self.assertEqual(kwargs, result)

    def test_list_ispname_param(self):
        """Test param as a list and ispname.
        """

        param = ['a', 'b', 'c']
        args, kwargs = self._update_params(param=param, ispname=True)

        self.assertEqual(args, param)
        self.assertFalse(kwargs)

    def test_dict_param(self):
        """Test param as a dict.
        """

        param = {'test': 'a', 'example': 'b'}
        kwargs = {'test': None}
        args, kwargs = self._update_params(param=param, kwargs=kwargs)

        self.assertFalse(args)
        self.assertEqual(kwargs, {'test': None, 'example': 'b'})

    def test_dict_update_param(self):
        """Test param as a dict.
        """

        param = {'test': 'a', 'example': 'b'}
        kwargs = {'test': None}
        args, kwargs = self._update_params(
            param=param, kwargs=kwargs, update=True
        )

        self.assertFalse(args)
        self.assertEqual(kwargs, {'test': 'a', 'example': 'b'})


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


class ContextTest(UTCase):
    """Test Context annotation.
    """

    def setUp(self):

        self.component = Controller()

    def tearDown(self):

        del self.component

    def _get_instance(self, param=None):
        """Create a class, annotate its constructor and returns a class
        instance.
        """

        class Test(object):

            @Context(param=param)
            def __init__(self, p0=None, p1=None, p2=None):

                self.p0 = p0
                self.p1 = p1
                self.p2 = p2

        result = C2BAnnotation.call_setter(component=self.component, impl=Test)

        return result

    def test_port(self):
        """Test to use Context with default param (None).
        """

        impl = self._get_instance()

        self.assertIs(impl.p0, self.component)
        self.assertIsNone(impl.p1)
        self.assertIsNone(impl.p2)

    def test_port_param(self):
        """Test to use Context with param equals self.port_name.
        """

        impl = self._get_instance(param='p1')

        self.assertIsNone(impl.p0)
        self.assertIs(impl.p1, self.component)
        self.assertIsNone(impl.p2)

    def test_port_list_param(self):
        """Test to use Context with a list param.
        """

        impl = self._get_instance(param=['p0', 'p2'])

        self.assertIs(impl.p0, self.component)
        self.assertIsNone(impl.p1)
        self.assertIs(impl.p2, self.component)

    def test_port_dict_param(self):
        """Test to use Context with a dict param.
        """

        impl = self._get_instance(param={'p0': None, 'p2': None})

        self.assertIs(impl.p0, self.component)
        self.assertIsNone(impl.p1)
        self.assertIs(impl.p2, self.component)


class TestPort(UTCase):
    """Test Port annotation.
    """

    def setUp(self):

        self.component = Controller()
        self.port_name = 'test'
        self.component[self.port_name] = self

    def tearDown(self):

        del self.component

    def _get_instance(self, param=None):
        """Create a class, annotate its constructor and returns a class
        instance.
        """

        class Test(object):

            @Port(param=param)
            def __init__(self, noparam=None, param=None):

                self.noparam = noparam
                self.param = param

        result = C2BAnnotation.call_setter(component=self.component, impl=Test)

        return result

    def test_port(self):
        """Test to use Port with default param (None).
        """

        impl = self._get_instance()

        self.assertIs(impl.noparam, self.component)
        self.assertIsNone(impl.param)

    def test_port_param(self):
        """Test to use Port with param equals self.port_name.
        """

        impl = self._get_instance(param=self.port_name)

        self.assertIs(impl.noparam, self)
        self.assertIsNone(impl.param)

    def test_port_list_param(self):
        """Test to use Port with a list param.
        """

        impl = self._get_instance(param=[None, self.port_name])

        self.assertIs(impl.noparam, self.component)
        self.assertIs(impl.param, self)

    def test_port_dict_param(self):
        """Test to use Port with a dict param.
        """

        impl = self._get_instance(param={'param': self.port_name})

        self.assertIsNone(impl.noparam)
        self.assertIs(impl.param, self)


class Controller2BAnnotationTest(UTCase):
    """Test Ctrl2BAnnotation annotation.
    """

    class ControllerTest(Controller):
        pass

    class Ann(Ctrl2BAnnotation):

        def get_ctrl_cls(self):

            return Controller2BAnnotationTest.ControllerTest

    def setUp(self):

        self.component = Controller()

    def tearDown(self):

        del self.component

    def _get_instance(self, param=None, force=False, error=None):
        """Create a class, annotate its constructor and returns a class
        instance.
        """

        result = None

        class Test(object):

            @Controller2BAnnotationTest.Ann(
                param=param, force=force, error=error
            )
            def __init__(self, p0=None, p1=None, p2=None):

                self.p0 = p0
                self.p1 = p1
                self.p2 = p2

        if error is not None:
            self.assertRaises(
                error,
                C2BAnnotation.call_setter,
                component=self.component,
                impl=Test
            )
        else:
            result = C2BAnnotation.call_setter(
                component=self.component, impl=Test
            )

        return result

    def test_default(self):
        """Test to use Ctrl2BAnnotation with default param (None).
        """

        impl = self._get_instance()

        self.assertIsNone(impl.p0)
        self.assertIsNone(impl.p1)
        self.assertIsNone(impl.p2)

    def test_port_param(self):
        """Test to use Ctrl2BAnnotation with param equals p1.
        """

        impl = self._get_instance(param='p1')

        self.assertIsNone(impl.p0)
        self.assertIsNone(impl.p1)
        self.assertIsNone(impl.p2)

    def test_port_list_param(self):
        """Test to use Ctrl2BAnnotation with a list param.
        """

        impl = self._get_instance(param=['p0', 'p2'])

        self.assertIsNone(impl.p0)
        self.assertIsNone(impl.p1)
        self.assertIsNone(impl.p2)

    def test_port_dict_param(self):
        """Test to use Ctrl2BAnnotation with a dict param.
        """

        impl = self._get_instance(param={'p0': None, 'p2': None})

        self.assertIsNone(impl.p0)
        self.assertIsNone(impl.p1)
        self.assertIsNone(impl.p2)

    def test_default_force(self):
        """Test to use Ctrl2BAnnotation with default param (None)
        and force.
        """

        impl = self._get_instance(force=True)

        self.assertIsInstance(
            impl.p0, Controller2BAnnotationTest.ControllerTest
        )
        self.assertIsNone(impl.p1)
        self.assertIsNone(impl.p2)

    def test_port_param_force(self):
        """Test to use Ctrl2BAnnotation with param equals p1 and force.
        """

        impl = self._get_instance(param='p1', force=True)

        self.assertIsNone(impl.p0)
        self.assertIsInstance(
            impl.p1, Controller2BAnnotationTest.ControllerTest
        )
        self.assertIsNone(impl.p2)

    def test_port_list_param_force(self):
        """Test to use Ctrl2BAnnotation with a list param and force.
        """

        impl = self._get_instance(param=['p0', 'p2'], force=True)

        self.assertIsInstance(
            impl.p0, Controller2BAnnotationTest.ControllerTest
        )
        self.assertIsNone(impl.p1)
        self.assertIsInstance(
            impl.p2, Controller2BAnnotationTest.ControllerTest
        )

    def test_port_dict_param_force(self):
        """Test to use Ctrl2BAnnotation with a dict param and force.
        """

        impl = self._get_instance(param={'p0': None, 'p2': None}, force=True)

        self.assertIsInstance(
            impl.p0, Controller2BAnnotationTest.ControllerTest
        )
        self.assertIsNone(impl.p1)
        self.assertIsInstance(
            impl.p2, Controller2BAnnotationTest.ControllerTest
        )

    def test_default_error(self):
        """Test to use Ctrl2BAnnotation with default param (None)
        and error.
        """

        self._get_instance(error=RuntimeError)

    def test_port_param_error(self):
        """Test to use Ctrl2BAnnotation with param equals p1 and error.
        """

        self._get_instance(param='p1', error=RuntimeError)

    def test_port_list_param_error(self):
        """Test to use Ctrl2BAnnotation with a list param and error.
        """

        self._get_instance(param=['p0', 'p2'], error=RuntimeError)

    def test_port_dict_param_error(self):
        """Test to use Ctrl2BAnnotation with a dict param and error.
        """

        self._get_instance(param={'p0': None, 'p2': None}, error=RuntimeError)


class ImplTest(UTCase):
    """Test Impl annotation.
    """

    def setUp(self):

        self.component = Controller()

    def tearDown(self):

        ImplController.unbind_from(self.component)
        del self.component

    def _get_instance(self, param=None, force=False, error=None):
        """Create a class, annotate its constructor and returns a class
        instance.
        """

        result = None

        class Test(object):

            @Impl(
                param=param, force=force, error=error
            )
            def __init__(self, p0=None, p1=None, p2=None):

                self.p0 = p0
                self.p1 = p1
                self.p2 = p2

        if error is not None:
            self.assertRaises(
                error,
                C2BAnnotation.call_setter,
                component=self.component,
                impl=Test
            )
        else:
            result = C2BAnnotation.call_setter(
                component=self.component, impl=Test
            )

        return result

    def test_default(self):
        """Test to use Impl with default param (None).
        """

        impl = self._get_instance()

        self.assertIsNone(impl.p0)
        self.assertIsNone(impl.p1)
        self.assertIsNone(impl.p2)

    def test_port_param(self):
        """Test to use Impl with param equals p1.
        """

        impl = self._get_instance(param='p1')

        self.assertIsNone(impl.p0)
        self.assertIsNone(impl.p1)
        self.assertIsNone(impl.p2)

    def test_port_list_param(self):
        """Test to use Impl with a list param.
        """

        impl = self._get_instance(param=['p0', 'p2'])

        self.assertIsNone(impl.p0)
        self.assertIsNone(impl.p1)
        self.assertIsNone(impl.p2)

    def test_port_dict_param(self):
        """Test to use Impl with a dict param.
        """

        impl = self._get_instance(param={'p0': None, 'p2': None})

        self.assertIsNone(impl.p0)
        self.assertIsNone(impl.p1)
        self.assertIsNone(impl.p2)

    def test_default_force(self):
        """Test to use Impl with default param (None)
        and force.
        """

        impl = self._get_instance(force=True)

        self.assertIsInstance(impl.p0, ImplController)
        self.assertIsNone(impl.p1)
        self.assertIsNone(impl.p2)

    def test_port_param_force(self):
        """Test to use Impl with param equals p1 and force.
        """

        impl = self._get_instance(param='p1', force=True)

        self.assertIsNone(impl.p0)
        self.assertIsInstance(impl.p1, ImplController)
        self.assertIsNone(impl.p2)

    def test_port_list_param_force(self):
        """Test to use Impl with a list param and force.
        """

        impl = self._get_instance(param=['p0', 'p2'], force=True)

        self.assertIsInstance(impl.p0, ImplController)
        self.assertIsNone(impl.p1)
        self.assertIsInstance(impl.p2, ImplController)

    def test_port_dict_param_force(self):
        """Test to use Impl with a dict param and force.
        """

        impl = self._get_instance(param={'p0': None, 'p2': None}, force=True)

        self.assertIsInstance(impl.p0, ImplController)
        self.assertIsNone(impl.p1)
        self.assertIsInstance(impl.p2, ImplController)

    def test_default_error(self):
        """Test to use Impl with default param (None)
        and error.
        """

        self._get_instance(error=RuntimeError)

    def test_port_param_error(self):
        """Test to use Impl with param equals p1 and error.
        """

        self._get_instance(param='p1', error=RuntimeError)

    def test_port_list_param_error(self):
        """Test to use Impl with a list param and error.
        """

        self._get_instance(param=['p0', 'p2'], error=RuntimeError)

    def test_port_dict_param_error(self):
        """Test to use Impl with a dict param and error.
        """

        self._get_instance(param={'p0': None, 'p2': None}, error=RuntimeError)


class TestGetterName(UTCase):
    """Test getter_name function.
    """

    def test_default(self):
        """Test to get a value from a default function.
        """

        def test():
            pass

        name = getter_name(test)

        self.assertEqual(name, 'test')

    def test_prefix(self):
        """Test to get a getter name from a function with getter_name prefix.
        """

        def gettest():
            pass

        name = getter_name(gettest)

        self.assertEqual(name, 'test')

    def test_prefix_(self):
        """Test to get a getter name from a function with getter_name prefix.
        """

        def get_test():
            pass

        name = getter_name(get_test)

        self.assertEqual(name, 'test')


class TestSetterName(UTCase):
    """Test setter_name function.
    """

    def test_default(self):
        """Test to get a value from a default function.
        """

        def test():
            pass

        name = setter_name(test)

        self.assertEqual(name, 'test')

    def test_prefix(self):
        """Test to get a setter name from a function with getter_name prefix.
        """

        def settest():
            pass

        name = setter_name(settest)

        self.assertEqual(name, 'test')

    def test_prefix_(self):
        """Test to get a setter name from a function with getter_name prefix.
        """

        def set_test():
            pass

        name = setter_name(set_test)

        self.assertEqual(name, 'test')


if __name__ == '__main__':
    main()
