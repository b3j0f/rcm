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
from b3j0f.rcm.core import Component
from b3j0f.rcm.ctl.core import Controller
from b3j0f.rcm.ctl.annotation import (
    CtlAnnotation, Ctl2CAnnotation, C2CtlAnnotation,
    C2Ctl2CAnnotation,
    CtlAnnotationInterceptor,
    SetPort, RemPort, Port,
    getter_name, setter_name
)


class BaseControllerTest(UTCase):

    def setUp(self):

        self.component = Component()
        Controller.APPLY(self.component)


class TestCtlAnnotation(BaseControllerTest):
    """Test CtlAnnotation.
    """

    class Ann(C2CtlAnnotation):

        def __init__(self, test, *args, **kwargs):

            super(TestCtlAnnotation.Ann, self).__init__(
                *args, **kwargs
            )

            self.test = test

        def apply(self, *args, **kwargs):

            self.test.count += 1

        def unapply(self, *args, **kwargs):

            self.test.count -= 1

    def setUp(self, *args, **kwargs):

        super(TestCtlAnnotation, self).setUp(*args, **kwargs)

        self.count = 0

    def test_apply(self):
        """Test apply method.
        """

        cls = str

        self.impl = cls()

        annotation = TestCtlAnnotation.Ann(self)
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

        annotation = TestCtlAnnotation.Ann(self)
        annotation(cls)
        annotation(cls.__format__, ctx=cls)

        CtlAnnotation.apply_on(
            component=None, impl=self.impl
        )
        self.assertEqual(self.count, 2)

    def test_unapply_from(self):
        """Test unapply_from method.
        """

        self.test_apply_on()

        CtlAnnotation.unapply_from(
            component=None,
            impl=self.impl
        )
        self.assertEqual(self.count, 0)


class TestCtl2CAnnotation(BaseControllerTest):
    """Test Ctl2CAnnotation.
    """

    def setUp(self, *args, **kwargs):

        super(TestCtl2CAnnotation, self).setUp(*args, **kwargs)

        self.count = 0

    class Ann(Ctl2CAnnotation):

        def process_result(self, result, **kwargs):

            result.count += 1

    def test_get_result(self):
        """Test process_result method.
        """

        annotation = TestCtl2CAnnotation.Ann()

        annotation.process_result(result=self)
        self.assertEqual(self.count, 1)

    def test_call_getter(self):
        """Test call_getter method.
        """

        class Test(object):

            def __init__(self, tb2ca=self):

                self.tb2ca = tb2ca

            @TestCtl2CAnnotation.Ann()
            def test(self):
                return self.tb2ca

        test = Test()
        Ctl2CAnnotation.call_getter(
            component=None, impl=test, getter=test.test
        )
        self.assertEqual(self.count, 1)

    def test_call_getters(self):
        """Test call_getters method.
        """

        class Test(object):

            def __init__(self, tb2ca=self):

                self.tb2ca = tb2ca

            @TestCtl2CAnnotation.Ann()
            def test(self):
                return self.tb2ca

        test = Test()
        Ctl2CAnnotation.call_getters(
            component=None, impl=test
        )
        self.assertEqual(self.count, 1)


class TestC2CtlAnnotation(BaseControllerTest):
    """Test C2CtlAnnotation.
    """

    class Ann(C2CtlAnnotation):

        def get_value(self, _upctx={}, *args, **kwargs):

            if 'count' not in _upctx:
                _upctx['count'] = 0
            _upctx['count'] += 1

            return _upctx['count']

    def test_get_value(self):
        """Test get_value method.
        """

        annotation = TestC2CtlAnnotation.Ann()

        value = annotation.get_value()
        self.assertIs(value, 1)

    def test_constructor_empty(self):
        """Test to inject a parameter in an empty constructor.
        """

        class Test(object):

            @TestC2CtlAnnotation.Ann()
            def __init__(self):
                pass

        self.assertRaises(
            C2CtlAnnotation.Error,
            C2CtlAnnotation.call_setter,
            component=None,
            impl=Test
        )

    def test_constructor(self):
        """Test to inject a parameter in a cls.
        """

        class Test(object):

            @TestC2CtlAnnotation.Ann()
            def __init__(self, test):

                self.test = test

        impl = C2CtlAnnotation.call_setter(component=None, impl=Test)

        self.assertIs(impl.test, 1)

    def test_constructor_name(self):
        """Test to inject a parameter in a cls with a dedicated name.
        """

        class Test(object):

            @TestC2CtlAnnotation.Ann(param='test')
            def __init__(self, a=2, b=1, test=None):

                self.test = test

        impl = C2CtlAnnotation.call_setter(component=None, impl=Test)

        self.assertIs(impl.test, 1)

    def test_routine_empty(self):
        """Test to inject a parameter in an empty routine.
        """

        class Test(object):

            @TestC2CtlAnnotation.Ann()
            def test(self):
                pass

        test = Test()

        self.assertRaises(
            C2CtlAnnotation.Error,
            C2CtlAnnotation.call_setter,
            component=None,
            impl=test,
            setter=test.test
        )

    def test_routine(self):
        """Test to inject a parameter in a routine.
        """

        class Test(object):

            @TestC2CtlAnnotation.Ann()
            def test(self, test):
                self.test = test

        test = Test()

        C2CtlAnnotation.call_setter(
            component=None, impl=test, setter=test.test
        )
        self.assertIs(test.test, 1)

    def test_routine_param(self):
        """Test to inject a parameter in a routine.
        """

        class Test(object):

            @TestC2CtlAnnotation.Ann(param='test')
            def test(self, a=0, b=1, test=None):

                self.a = a
                self.b = b
                self.test = test

        test = Test()

        C2CtlAnnotation.call_setter(
            component=None, impl=test, setter=test.test
        )
        self.assertIs(test.a, 0)
        self.assertIs(test.b, 1)
        self.assertIs(test.test, 1)

    def test_call_setters(self):
        """Test call_setters method.
        """

        class Ann(C2CtlAnnotation):

            def get_value(self, _upctx, *args, **kwargs):

                if 'count' not in _upctx:
                    _upctx['count'] = 0

                _upctx['count'] += 1

                return _upctx['count']

        class Test(object):

            def __init__(self):
                self.count = 1

            @Ann()
            def test0(self, a):
                self.count += a * 10

            @Ann()
            def test1(self, a):
                self.count += a * 100

            def test2(self, a):
                self.count += a * 1000

        annotation = Ann()
        annotation(Test.test2)

        test = Test()

        C2CtlAnnotation.call_setters(component=None, impl=test)

        self.assertEqual(test.count, 1111)

    def test_multi_annotations(self):
        """Test with multi C2CtlAnnotations on the same routine.
        """

        class Ann1(C2CtlAnnotation):
            def get_value(self, *args, **kwargs):
                return 1

        class Ann2(C2CtlAnnotation):
            def get_value(self, *args, **kwargs):
                return 2

        def assertMultiAnnotation(
            p1=None, p2=None, a=None, b=None, c=None, d=None
        ):
            """Annotate a routine with alltime Ann1 and Ann2 with respective
            parameters p1 and p2, then assert values of a Test instance
            with input a, b, c, d.
            """
            class Test(object):

                @Ann1(param=p1)
                @Ann2(param=p2)
                def __init__(self, a=None, b=None, c=None, d=None):
                    super(Test, self).__init__()
                    self.a = a
                    self.b = b
                    self.c = c
                    self.d = d

            test = C2CtlAnnotation.call_setter(component=None, impl=Test)

            self.assertIs(a, test.a)
            self.assertIs(b, test.b)
            self.assertIs(c, test.c)
            self.assertIs(d, test.d)

        # check if varargs is correctly filled
        assertMultiAnnotation(a=1, b=2)
        # check if varargs and kwargs are in a conflict
        self.assertRaises(
            C2CtlAnnotation.Error,
            assertMultiAnnotation,
            p1='a'
        )
        # check if named param is ok
        assertMultiAnnotation(p1='b', a=2, b=1)
        # check if a list of param names are ok
        assertMultiAnnotation(p1=['b', 'c'], a=2, b=1, c=1)

    def _get_parameterized_class(self):

        class Test(object):

            def set_value(self, *args, **kwargs):

                self.args = args
                self.kwargs = kwargs

        return Test

    def _get_class_w_ann(self, param=None, ispname=False, update=True):

        Test = self._get_parameterized_class()

        class TestAnn(C2CtlAnnotation):

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

        impl = C2CtlAnnotation.call_setter(
            component=None, impl=Test, force=True
        )

        self.assertIsInstance(impl, Test)

    def _update_params(
        self, param=None, ispname=False, update=False,
        args=None, kwargs=None, **ks
    ):
        """Call C2CtlAnnotation._update_params with input parameters and
        return
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

        impl = C2CtlAnnotation.call_setter(component=None, impl=Test)

        self.assertIsNone(impl)

    def test_update_params_none(self):
        """Test with param is None.
        """

        args, kwargs = self._update_params()

        self.assertEqual(args, [self])
        self.assertFalse(kwargs)

    def test_update_params_none_ispname(self):
        """Test with param is None and ispname.
        """

        args, kwargs = self._update_params(ispname=True)

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


class TestC2Ctl2CAnnotation(BaseControllerTest):
    """Test C2Ctl2CAnnotation.
    """

    class C2Ctl2C(C2Ctl2CAnnotation):

        def __init__(self, tcbc, *args, **kwargs):

            super(TestC2Ctl2CAnnotation.C2Ctl2C, self).__init__(
                *args, **kwargs
            )

            self.tcbc = tcbc

        def get_value(self, *args, **kwargs):

            self.tcbc.count_value += 1

            return self.tcbc

        def process_result(self, result, *args, **kwargs):

            result.count_result += 1

    def setUp(self, *args, **kwargs):

        super(TestC2Ctl2CAnnotation, self).setUp(*args, **kwargs)

        self.count_value = 0
        self.count_result = 0

    def test_routine(self):

        class Test(object):

            @TestC2Ctl2CAnnotation.C2Ctl2C(self, param='test')
            def test(self, a=0, test=None):
                self._test = test
                return test

        test = Test()

        C2CtlAnnotation.call_setters(
            component=None, impl=test, call_getters=True
        )
        self.assertEqual(self.count_value, 1)
        self.assertEqual(self.count_result, 1)
        self.assertIs(test._test, self)


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

        result = C2CtlAnnotation.call_setter(
            component=self.component, impl=Test
        )

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
        """Test to get a getter name from a function with getter_name prefix
        and _.
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
        """Test to get a setter name from a function with getter_name prefix
        and _.
        """

        def set_test():
            pass

        name = setter_name(set_test)

        self.assertEqual(name, 'test')


class TestC2CtlAnnotationInterceptor(UTCase):
    """Test CtlAnnotationInterceptor annotation.
    """

    class C2CtlAI(CtlAnnotationInterceptor):
        """CtlAnnotationInterceptor test class.
        """

        def get_target_ctx(self, component, *args, **kwargs):
            """Intercept component contains method.
            """

            return component.contains, component

    def setUp(self, *args, **kwargs):

        super(TestC2CtlAnnotationInterceptor, self).setUp(*args, **kwargs)

        self.component = Component()
        self.controller = Controller.APPLY(self.component)

        class ImplTest(Controller):
            """Implementation test class.
            """

            def __init__(self, test):

                super(ImplTest, self).__init__()

                self.test = test

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.ALLTIME
            )
            def test_alltime(self):
                """Test alltime.
                """
                self.test.before += 1
                self.test.after += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.ALLTIME
            )
            def test_alltime_default(self, _result):
                """Test with alltime and default behavior.

                :param _result: intercepted function result.
                """
                if _result:
                    self.test.after += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.ALLTIME,
                vparams=['when', 'result']
            )
            def test_alltime_v(self, _when, _result):
                """Test alltime with vparams.
                """
                if _when == CtlAnnotationInterceptor.BEFORE:
                    self.test.before += 1
                elif _result:
                    self.test.after += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.ALLTIME,
                vparams=['when', 'result']
            )
            def test_alltime_vv(self, *args):
                if args[0] == CtlAnnotationInterceptor.BEFORE:
                    self.test.before += 1
                elif args[1]:
                    self.test.after += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.ALLTIME,
                kparams={'when': '_when', 'result': '_result'}
            )
            def test_alltime_k(self, _when, _result):
                if _when == CtlAnnotationInterceptor.BEFORE:
                    self.test.before += 1
                elif _result:
                    self.test.after += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.ALLTIME,
                kparams={'when': '_when', 'result': '_result'}
            )
            def test_alltime_kk(self, **kwargs):
                if kwargs['_when'] == CtlAnnotationInterceptor.BEFORE:
                    self.test.before += 1
                elif kwargs['_result']:
                    self.test.after += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.BEFORE
            )
            def test_before(self):
                self.test.before += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.BEFORE
            )
            def test_before_default(self, _result):
                """Test with before and default behavior.
                """
                if _result:
                    self.test.before += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.BEFORE, vparams=['when']
            )
            def test_before_v(self, _when):
                if _when == CtlAnnotationInterceptor.BEFORE:
                    self.test.before += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.BEFORE, vparams=['when']
            )
            def test_before_vv(self, *args):
                if args[0] == CtlAnnotationInterceptor.BEFORE:
                    self.test.before += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.BEFORE,
                kparams={'when': '_when'}
            )
            def test_before_k(self, _when):
                if _when == CtlAnnotationInterceptor.BEFORE:
                    self.test.before += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.BEFORE,
                kparams={'when': '_when'}
            )
            def test_before_kk(self, **kwargs):
                if kwargs['_when'] == CtlAnnotationInterceptor.BEFORE:
                    self.test.before += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.AFTER
            )
            def test_after(self):
                self.test.after += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.AFTER
            )
            def test_after_default(self, _result):
                """Test with after and default behavior.
                """
                if _result:
                    self.test.after += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.AFTER,
                vparams=['when', 'result']
            )
            def test_after_v(self, _when, _result):
                if _when == CtlAnnotationInterceptor.AFTER and _result:
                    self.test.after += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.AFTER,
                vparams=['when', 'result']
            )
            def test_after_vv(self, *args):
                if args[0] == CtlAnnotationInterceptor.AFTER and args[1]:
                    self.test.after += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.AFTER,
                kparams={'when': '_when', 'result': '_result'}
            )
            def test_after_k(self, _when, _result):
                if _when == CtlAnnotationInterceptor.AFTER and _result:
                    self.test.after += 1

            @TestC2CtlAnnotationInterceptor.C2CtlAI(
                when=CtlAnnotationInterceptor.AFTER,
                kparams={'when': '_when', 'result': '_result'}
            )
            def test_after_kk(self, **kwargs):
                if (
                    kwargs['_when'] == CtlAnnotationInterceptor.AFTER
                    and kwargs['_result']
                ):
                    self.test.after += 1

        self.before = 0
        self.after = 0

        self.component['test'] = True

        self.controller = ImplTest.APPLY(self.component, self)

    def test(self):

        self.assertEqual(self.before, 0)
        self.assertEqual(self.after, 0)

        self.component.contains(self.controller)

        self.assertEqual(self.before, 11)
        self.assertEqual(self.after, 13)


class TestSetPort(UTCase):
    """Test SetPort annotation.
    """

    def setUp(self, *args, **kwargs):

        super(TestSetPort, self).setUp(*args, **kwargs)

        self.component = Component()

        class ImplTest(Controller):
            """Implementation test class.
            """

            def __init__(self, test, *args, **kwargs):

                super(ImplTest, self).__init__(*args, **kwargs)

                self.test = test

            def check_params(self, *args, **kwargs):

                result = (
                    (args == ('name', 'port'))
                    or
                    (
                        kwargs
                        and kwargs['_name'] == 'name'
                        and kwargs['_port'] == 'port'
                    )
                )

                return result

            @SetPort(when=CtlAnnotationInterceptor.ALLTIME)
            def test_alltime(self):
                self.test.before += 1
                self.test.after += 1

            @SetPort(when=CtlAnnotationInterceptor.ALLTIME)
            def test_alltime_default(self, _result):
                if _result:
                    self.test.after += 1

            @SetPort(
                when=CtlAnnotationInterceptor.ALLTIME,
                vparams=['when', 'result', 'name', 'port']
            )
            def test_alltime_v(self, _when, _result, _name, _port):
                if self.check_params(_name, _port):
                    if _when == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1
                    elif _result:
                        self.test.after += 1

            @SetPort(
                when=CtlAnnotationInterceptor.ALLTIME,
                vparams=['when', 'result', 'name', 'port']
            )
            def test_alltime_vv(self, *args):
                if self.check_params(*args[2:]):
                    if args[0] == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1
                    elif args[1]:
                        self.test.after += 1

            @SetPort(
                when=CtlAnnotationInterceptor.ALLTIME,
                kparams={
                    'when': '_when',
                    'result': '_result',
                    'name': '_name',
                    'port': '_port'
                }
            )
            def test_alltime_k(self, _when, _result, _name, _port):
                if self.check_params(_name, _port):
                    if _when == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1
                    elif _result:
                        self.test.after += 1

            @SetPort(
                when=CtlAnnotationInterceptor.ALLTIME,
                kparams={
                    'when': '_when',
                    'result': '_result',
                    'name': '_name',
                    'port': '_port'
                }
            )
            def test_alltime_kk(self, **kwargs):
                if self.check_params(**kwargs):
                    if kwargs['_when'] == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1
                    elif kwargs['_result']:
                        self.test.after += 1

            @SetPort(
                when=CtlAnnotationInterceptor.BEFORE
            )
            def test_before(self):
                self.test.before += 1

            @SetPort(when=CtlAnnotationInterceptor.BEFORE)
            def test_before_default(self, _result):
                if _result:
                    self.test.after += 1

            @SetPort(
                when=CtlAnnotationInterceptor.BEFORE,
                vparams=['when', 'name', 'port']
            )
            def test_before_v(self, _when, _name, _port):
                if self.check_params(_name, _port):
                    if _when == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1

            @SetPort(
                when=CtlAnnotationInterceptor.BEFORE,
                vparams=['when', 'name', 'port']
            )
            def test_before_vv(self, *args):
                if self.check_params(*args[1:]):
                    if args[0] == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1

            @SetPort(
                when=CtlAnnotationInterceptor.BEFORE,
                kparams={
                    'when': '_when',
                    'name': '_name',
                    'port': '_port'
                }
            )
            def test_before_k(self, _when, _name, _port):
                if self.check_params(_name, _port):
                    if _when == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1

            @SetPort(
                when=CtlAnnotationInterceptor.BEFORE,
                kparams={
                    'when': '_when',
                    'name': '_name',
                    'port': '_port'
                }
            )
            def test_before_kk(self, **kwargs):
                if self.check_params(**kwargs):
                    if kwargs['_when'] == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1

            @SetPort(
                when=CtlAnnotationInterceptor.AFTER
            )
            def test_after(self):
                self.test.after += 1

            @SetPort(when=CtlAnnotationInterceptor.AFTER)
            def test_after_default(self, _result):
                if _result:
                    self.test.after += 1

            @SetPort(
                when=CtlAnnotationInterceptor.AFTER,
                vparams=['when', 'result', 'name', 'port']
            )
            def test_after_v(self, _when, _result, _name, _port):
                if self.check_params(_name, _port):
                    if _when == CtlAnnotationInterceptor.AFTER and _result:
                        self.test.after += 1

            @SetPort(
                when=CtlAnnotationInterceptor.AFTER,
                vparams=['when', 'result', 'name', 'port']
            )
            def test_after_vv(self, *args):
                if self.check_params(*args[2:]):
                    if args[0] == CtlAnnotationInterceptor.AFTER and args[1]:
                        self.test.after += 1

            @SetPort(
                when=CtlAnnotationInterceptor.AFTER,
                kparams={
                    'when': '_when',
                    'result': '_result',
                    'name': '_name',
                    'port': '_port'
                }
            )
            def test_after_k(self, _when, _result, _name, _port):
                if self.check_params(_name, _port):
                    if _when == CtlAnnotationInterceptor.AFTER and _result:
                        self.test.after += 1

            @SetPort(
                when=CtlAnnotationInterceptor.AFTER,
                kparams={
                    'when': '_when',
                    'result': '_result',
                    'name': '_name',
                    'port': '_port'
                }
            )
            def test_after_kk(self, **kwargs):
                if self.check_params(**kwargs):
                    if (
                        kwargs['_when'] == CtlAnnotationInterceptor.AFTER
                        and kwargs['_result']
                    ):
                        self.test.after += 1

        self.before = 0
        self.after = 0

        self.component['test'] = True

        self.controller = ImplTest.APPLY(self.component, self)

    def test(self):

        self.assertEqual(self.before, 0)
        self.assertEqual(self.after, 0)

        self.component.set_port(name='name', port='port')

        self.assertEqual(self.before, 11)
        self.assertEqual(self.after, 13)


class TestRemPort(UTCase):
    """Test RemPort annotation.
    """

    def setUp(self, *args, **kwargs):

        super(TestRemPort, self).setUp(*args, **kwargs)

        self.component = Component()

        class ImplTest(Controller):
            """Implementation test class.
            """

            def __init__(self, test):

                super(ImplTest, self).__init__()

                self.test = test

            def check_params(self, *args, **kwargs):

                result = (
                    (args == ('test',))
                    or
                    (
                        kwargs
                        and kwargs['_name'] == 'test'
                    )
                )

                return result

            @RemPort(when=CtlAnnotationInterceptor.ALLTIME)
            def test_alltime(self):
                self.test.before += 1
                self.test.after += 1

            @RemPort(
                when=CtlAnnotationInterceptor.ALLTIME,
                vparams=['when', 'result', 'name']
            )
            def test_alltime_v(self, _when, _result, _name):
                if self.check_params(_name):
                    if _when == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1
                    elif _result:
                        self.test.after += 1

            @RemPort(
                when=CtlAnnotationInterceptor.ALLTIME,
                vparams=['when', 'result', 'name']
            )
            def test_alltime_vv(self, *args):
                if self.check_params(*args[2:]):
                    if args[0] == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1
                    elif args[1]:
                        self.test.after += 1

            @RemPort(
                when=CtlAnnotationInterceptor.ALLTIME,
                kparams={
                    'when': '_when',
                    'result': '_result',
                    'name': '_name'
                }
            )
            def test_alltime_k(self, _when, _result, _name):
                if self.check_params(_name):
                    if _when == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1
                    elif _result:
                        self.test.after += 1

            @RemPort(
                when=CtlAnnotationInterceptor.ALLTIME,
                kparams={
                    'when': '_when',
                    'result': '_result',
                    'name': '_name'
                }
            )
            def test_alltime_kk(self, **kwargs):
                if self.check_params(**kwargs):
                    if kwargs['_when'] == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1
                    elif kwargs['_result']:
                        self.test.after += 1

            @RemPort(
                when=CtlAnnotationInterceptor.BEFORE
            )
            def test_before(self):
                self.test.before += 1

            @RemPort(
                when=CtlAnnotationInterceptor.BEFORE,
                vparams=['when', 'name']
            )
            def test_before_v(self, _when, _name):
                if self.check_params(_name):
                    if _when == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1

            @RemPort(
                when=CtlAnnotationInterceptor.BEFORE,
                vparams=['when', 'name']
            )
            def test_before_vv(self, *args):
                if self.check_params(*args[1:]):
                    if args[0] == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1

            @RemPort(
                when=CtlAnnotationInterceptor.BEFORE,
                kparams={
                    'when': '_when',
                    'name': '_name'
                }
            )
            def test_before_k(self, _when, _name):
                if self.check_params(_name):
                    if _when == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1

            @RemPort(
                when=CtlAnnotationInterceptor.BEFORE,
                kparams={
                    'when': '_when',
                    'name': '_name'
                }
            )
            def test_before_kk(self, **kwargs):
                if self.check_params(**kwargs):
                    if kwargs['_when'] == CtlAnnotationInterceptor.BEFORE:
                        self.test.before += 1

            @RemPort(
                when=CtlAnnotationInterceptor.AFTER
            )
            def test_after(self):
                self.test.after += 1

            @RemPort(
                when=CtlAnnotationInterceptor.AFTER,
                vparams=['when', 'result', 'name']
            )
            def test_after_v(self, _when, _result, _name):
                if self.check_params(_name):
                    if _when == CtlAnnotationInterceptor.AFTER and _result:
                        self.test.after += 1

            @RemPort(
                when=CtlAnnotationInterceptor.AFTER,
                vparams=['when', 'result', 'name']
            )
            def test_after_vv(self, *args):
                if self.check_params(*args[2:]):
                    if args[0] == CtlAnnotationInterceptor.AFTER and args[1]:
                        self.test.after += 1

            @RemPort(
                when=CtlAnnotationInterceptor.AFTER,
                kparams={
                    'when': '_when',
                    'result': '_result',
                    'name': '_name'
                }
            )
            def test_after_k(self, _when, _result, _name):
                if self.check_params(_name):
                    if _when == CtlAnnotationInterceptor.AFTER and _result:
                        self.test.after += 1

            @RemPort(
                when=CtlAnnotationInterceptor.AFTER,
                kparams={
                    'when': '_when',
                    'result': '_result',
                    'name': '_name'
                }
            )
            def test_after_kk(self, **kwargs):
                if self.check_params(**kwargs):
                    if (
                        kwargs['_when'] == CtlAnnotationInterceptor.AFTER
                        and kwargs['_result']
                    ):
                        self.test.after += 1

        self.before = 0
        self.after = 0

        self.component['test'] = True

        self.controller = ImplTest.APPLY(self.component, self)

    def test(self):

        self.assertEqual(self.before, 0)
        self.assertEqual(self.after, 0)

        self.component.remove_port(name='test')

        self.assertEqual(self.before, 11)
        self.assertEqual(self.after, 11)


if __name__ == '__main__':
    main()
