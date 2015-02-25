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
from b3j0f.rcm.controller.core import Controller
from b3j0f.rcm.controller.impl import (
    ImplController, Impl, ImplAnnotation, ParameterizedImplAnnotation, Context
)


class ImplControllerTest(UTCase):
    """Test impl controller.
    """

    def setUp(self):

        self.controller = ImplController()

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
        """Test impl.
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

    def test_update(self):
        """Test to update the controller.
        """

        class TestImplAnnotation(ImplAnnotation):
            """
            """

if __name__ == '__main__':
    main()
