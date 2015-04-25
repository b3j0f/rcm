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
from b3j0f.rcm.controller.port import Interface, Port


class InterfaceTest(UTCase):
    """Test Interface.
    """

    def setUp(self):

        self.interface = Interface()

    def test_none(self):
        """Test to set a None value.
        """

        self.interface = None
        self.assertNone(self.interface.value, None)
        self.assertIs(self.interface.pvalue, object)


class PortTest(UTCase):
    """
    """

    class TestPort(Port):

        def get_resource(self):

            return self

    def setUp(self):

        self.port = PortTest.TestPort()

    def test_interfaces(self):
        """Test to set and get interfaces.
        """

        # check no interfaces
        self.assertEqual(self.port.interfaces, [object])

        # check one interface
        interfaces = int
        self.port.interfaces = interfaces
        self.assertEqual(self.port.interfaces, [interfaces])

        # check one interface name
        interfaces = getpath(int)
        self.port.interfaces = interfaces
        self.assertEqual(self.port.interfaces, [int])

        # check many interfaces
        interfaces = [int, str]
        self.port.interfaces = interfaces
        self.assertEqual(self.port.interfaces, interfaces)

        # check set interfaces
        interfaces = {int, str}
        self.port.interfaces = interfaces
        self.assertEqual(self.port.interfaces, list(interfaces))

        # interfaces is not a class
        self.assertRaises(TypeError, setattr, self.port, 'interfaces', 3)
        self.assertRaises(ImportError, setattr, self.port, 'interfaces', "")

    def test_resource(self):
        """Test port proxy.
        """

        class Resource(object):
            def apply(self):
                return 1
        resource = Resource()

        resource_name = 'resource'

        # check object resource
        self.port[resource_name] = resource
        self.assertEqual(self.port[resource_name], resource)
        resources = self.port.resources
        self.assertEqual(resources, {resource_name: resource})

        # check port resource
        port = Port()
        self.port[resource_name] = port
        self.assertEqual(self.port[resource_name], port)
        resources = self.port.resources
        self.assertEqual(resources, {resource_name: port})

        # check same port as a second resource
        second_resource_name = 'resource2'
        self.port[second_resource_name] = port
        self.assertEqual(self.port[second_resource_name], port)
        resources = self.port.resources
        self.assertEqual(
            resources, {resource_name: port, second_resource_name: port}
        )


    def test_proxy(self):
        """Test get proxy.
        """


if __name__ == '__main__':
    main()
