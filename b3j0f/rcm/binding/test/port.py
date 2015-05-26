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
from b3j0f.rcm.binding.port import ProxySet, Port
from b3j0f.rcm.binding.core import Interface, Resource


class PortTest(UTCase):
    """Test Port.
    """

    def test_sup(self):
        """Test to put more resources than granted.
        """

        port = Port(sup=2)

        port.set_port(port)
        port.set_port(port)
        self.assertRaises(Port.PortError, port.set_port, port)

        resources = port.get_resources()
        self.assertEqual(len(resources), 2)

    def test_inf(self):
        """Test to put less resources than granted.
        """

        port = Port(inf=2)

        self.assertRaises(Port.PortError, port.set_port, port)
        port.set_port(port)

        resources = port.get_resources()
        self.assertEqual(len(resources), 2)

    def test_check_resource(self):
        """Test the check_resource method.
        """

        port = Port()

        port2 = Port()

        # check with default interfaces
        checked = port.check_resource(port2)
        self.assertTrue(checked)

        # uncheck with int interface
        port.itfs = (Interface(value=int),)
        checked = port.check_resource(port2)
        self.assertFalse(checked)

        # check back with int interface
        port2.itfs = (Interface(value=int),)
        checked = port.check_resource(port2)
        self.assertTrue(checked)

        # check back with object interface
        port.itfs = (Interface(),)
        checked = port.check_resource(port2)
        self.assertTrue(checked)

    def test_multiple(self):
        """Test multiple port.
        """

        port = Port(multiple=True)

        proxy = port.proxy
        self.assertIsInstance(proxy, ProxySet)
        self.assertFalse(proxy)

        port2 = Port()
        port.set_port(port2)
        proxy = port.proxy
        self.assertIsInstance(proxy, ProxySet)
        self.assertFalse(proxy, proxy)

        resource = Resource(proxy=object)
        port.set_port(resource)
        proxy = port.proxy
        self.assertIsInstance(proxy, ProxySet)
        self.assertTrue(proxy, proxy)
        self.assertEquals(len(proxy), 1)

        port2.set_port(resource)
        proxy = port.proxy
        self.assertIsInstance(proxy, ProxySet)
        self.assertTrue(proxy, proxy)
        self.assertEquals(len(proxy), 2)

        port2['test'] = resource
        proxy = port.proxy
        self.assertIsInstance(proxy, ProxySet)
        self.assertTrue(proxy, proxy)
        self.assertEquals(len(proxy), 3)

        port2['test'] = resource
        proxy = port.proxy
        self.assertIsInstance(proxy, ProxySet)
        self.assertTrue(proxy, proxy)
        self.assertEquals(len(proxy), 3)

    def test_notmultiple(self):
        """Test not multiple port.
        """

        port = Port(multiple=False)

        proxy = port.proxy
        self.assertIsNone(proxy)

    def test_renewproxy(self):
        """Test _renewproxy method.
        """

        port = Port()
        port2 = Port()

        port.set_port(port2)


class TestProxySet(UTCase):
    """Test ProxySet.
    """

    def setUp(self):

        self.proxyset = ProxySet()


if __name__ == '__main__':
    main()
