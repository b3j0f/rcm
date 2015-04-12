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
from b3j0f.rcm.controller.proxy import Proxy, Binding


class BindingTest(UTCase):
    """
    """

    class TestBinding(Binding):

        def get_resource(self):

            return self

    def setUp(self):

        self.binding = BindingTest.TestBinding(proxy=None)

    def test_get_name(self):
        """Test get_name class method.
        """

        class_name = BindingTest.TestBinding.get_name()

        instance_name = self.binding.get_name()

        self.assertEqual(class_name, instance_name)

        self.assertEqual(class_name, BindingTest.TestBinding.__name__.lower())

    def test_get_resource(self):
        """Test Binding.get_resource method.
        """

        resource = self.binding.get_resource()

        self.assertIs(self.binding, resource)


class TestProxy(UTCase):
    """Test Proxy class.
    """

    class ProxyTest(Proxy):

        pass

    def setUp(self):

        self.proxy = TestProxy.ProxyTest()

    def test_get_resource(self):

        pass

    def test_check_resource(self):
        """Test to check a resource with no interfaces.
        """

        pass


if __name__ == '__main__':
    main()
