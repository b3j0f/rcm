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
    ImplController, ImplAnnotation
)


class ImplControllerTest(UTCase):
    """Test impl controller.
    """

    class TestImplAnnotation(ImplAnnotation):

        def __init__(self, implcontrollertest, *args, **kwargs):

            super(ImplControllerTest.TestImplAnnotation, self).__init__(
                *args, **kwargs
            )

            self.implcontrollertest = implcontrollertest

        def apply(self, *args, **kwargs):

            self.implcontrollertest.count += 1

        def unapply(self, *args, **kwargs):

            self.implcontrollertest.count -= 1

    def setUp(self):

        self.count = 0
        self.controller = ImplController()
        Controller.bind_all(self.controller, self.controller)

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

        annotation = ImplControllerTest.TestImplAnnotation(self)
        annotation(object)
        annotation(object.__hash__, ctx=impl.__class__)

        self.controller.impl = impl
        self.assertIs(self.controller.impl, impl)
        self.assertIs(self.controller.impl.__class__, object)
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

        @ImplControllerTest.TestImplAnnotation(self)
        class TestImpl(object):

            @ImplControllerTest.TestImplAnnotation(self)
            def __init__(self, a, b=1):

                self.a = a
                self.b = b

        self.controller.cls = TestImpl

        self.assertRaises(
            ImplController.ImplError, self.controller.instantiate
        )

        new_impl = self.controller.instantiate(params={'a': 0})
        self.assertEqual(new_impl.a, 0)
        self.assertEqual(new_impl.b, 1)
        self.assertEqual(self.count, 2)

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

if __name__ == '__main__':
    main()
