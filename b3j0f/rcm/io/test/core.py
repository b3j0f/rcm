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

"""Test the module b3j0f.rcm.io.core.
"""

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.rcm.core import Component
from b3j0f.rcm.io.proxy import ProxySet
from b3j0f.rcm.io.core import Port
from b3j0f.rcm.io.desc import Interface


class PortTest(UTCase):
    """Test Port.
    """

    def test_sup(self):
        """Test to put more resources than granted.
        """

        port = Port(sup=2)

        # assert new port is not port
        self.assertRaises(Port.PortError, port.set_port, port)
        # assert sup
        port.set_port(Port())
        port.set_port(Port())
        self.assertRaises(Port.PortError, port.set_port, Port())

        resources = port.resources
        self.assertEqual(len(resources), 2)

    def test_inf(self):
        """Test to put less resources than granted.
        """

        port = Port(inf=2)
        # assert new port is not port
        self.assertRaises(Port.PortError, port.set_port, port)
        # assert inf
        self.assertRaises(Port.PortError, port.set_port, Port())
        port.set_port(Port())

        resources = port.resources
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
        port.set_port(port=port2)
        proxy = port.proxy
        self.assertIsInstance(proxy, ProxySet)
        self.assertFalse(proxy)

        resource = Port(resource=object())
        port.set_port(port=resource)
        proxy = port.proxy
        self.assertIsInstance(proxy, ProxySet)
        self.assertTrue(proxy)
        self.assertEqual(len(proxy), 1)

        port2.set_port(port=resource)
        proxy = port.proxy
        self.assertIsInstance(proxy, ProxySet)
        self.assertTrue(proxy)
        self.assertEqual(len(proxy), 2)

        port2['test'] = resource
        proxy = port.proxy
        self.assertIsInstance(proxy, ProxySet)
        self.assertTrue(proxy, proxy)
        self.assertEqual(len(proxy), 3)

        port2['test'] = resource
        proxy = port.proxy
        self.assertIsInstance(proxy, ProxySet)
        self.assertTrue(proxy, proxy)
        self.assertEqual(len(proxy), 3)

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

    def test_iokind(self):
        """Test iokind.
        """

        port = Port()

        self.assertEqual(port.iokind, Port.DEFAULT_IOKIND)
        self.assertTrue(port.isinput)
        self.assertTrue(port.isoutput)

        port.iokind = Port.INPUT
        self.assertEqual(port.iokind, Port.INPUT)
        self.assertTrue(port.isinput)
        self.assertFalse(port.isoutput)

        port.iokind = Port.OUTPUT
        self.assertEqual(port.iokind, Port.OUTPUT)
        self.assertFalse(port.isinput)
        self.assertTrue(port.isoutput)

    def test_INPUTS_OUTPUTS(self):
        """Test INPUTS class method.
        """

        cmpt = Component(
            namedports={
                'i0': Port(iokind=Port.INPUT),
                'i1': Port(iokind=Port.INPUT),
                'o0': Port(iokind=Port.OUTPUT),
                'o1': Port(iokind=Port.OUTPUT),
                'io0': Port(),
                'io1': Port(),
            }
        )

        def assertPorts(names, _input=True):
            """Assert INPUTS/OUTPUTS result with input names.

            :param list names: port names to check.
            :param bool _input: if True (default) assert input ports. Otherwise
                , output ports.
            """
            func_name = 'INPUTS' if _input else 'OUTPUTS'
            ports = getattr(Port, func_name)(component=cmpt)
            self.assertEqual(len(ports), 4)
            for name in names:
                port = ports.pop(name)
                attrname = 'isinput' if _input else 'isoutput'
                self.assertTrue(getattr(port, attrname))

        assertPorts(names=['i0', 'i1', 'io0', 'io1'])
        assertPorts(names=['o0', 'o1', 'io0', 'io1'], _input=False)


if __name__ == '__main__':
    main()
