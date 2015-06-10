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
from b3j0f.rcm.core import Component
from b3j0f.rcm.nf.core import Controller
from b3j0f.rcm.nf.annotation import C2CtrlAnnotation
from b3j0f.rcm.nf.impl import (
    ImplController, Impl, Stateless, Context
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
                C2CtrlAnnotation.call_setter,
                component=self.component,
                impl=Test
            )
        else:
            result = C2CtrlAnnotation.call_setter(
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


class TestStateless(UTCase):

    def setUp(self, *args, **kwargs):

        super(TestStateless, self).setUp(*args, **kwargs)

        self.component = Component()
        self.controller = ImplController.bind_to(self.component)

    def test_change(self):
        """Apply Stateless.
        """

        # ensure controller stateful is True
        self.assertTrue(self.controller.stateful)

        # annotate a cls implementation
        @Stateless()
        class Test(object):
            pass

        # renew the impl and assert stateful is False
        self.controller.impl = Test()
        self.assertFalse(self.controller.stateful)

        # unapply annotation and assert stateful is True
        self.controller.impl = None
        self.assertTrue(self.controller.stateful)

    def test_change_and_recover(self):
        """Apply stateless and recover its value after unapplying it.
        """

        # ensure controller stateful is False
        self.controller.stateful = False
        self.assertFalse(self.controller.stateful)

        # annotate a cls implementation
        @Stateless()
        class Test(object):
            pass

        # renew the impl and assert stateful is False
        self.controller.impl = Test()
        self.assertFalse(self.controller.stateful)

        # unapply annotation and assert stateful is still False
        self.controller.impl = None
        self.assertFalse(self.controller.stateful)


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

        result = C2CtrlAnnotation.call_setter(
            component=self.component, impl=Test
        )

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


if __name__ == '__main__':
    main()
