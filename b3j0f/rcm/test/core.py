#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2014 Jonathan Labéjof <jonathan.labejof@gmail.com>
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


class ComponentTest(UTCase):

    class TestPort(Component):

        def __init__(self, componentest, *args, **kwargs):

            super(ComponentTest.TestPort, self).__init__(*args, **kwargs)

            self.componentest = componentest

        def _onbind(self, component, name, *args, **kwargs):

            super(ComponentTest.TestPort, self)._onbind(
                component=component, name=name, *args, **kwargs
            )

            self.componentest.bindcount -= 1

        def _onunbind(self, component, name, *args, **kwargs):

            super(ComponentTest.TestPort, self)._onunbind(
                component=component, name=name, *args, **kwargs
            )

            self.componentest.unbindcount -= 1

    def setUp(self):

        self.component = Component()
        self.namedports = {
            'test': ComponentTest.TestPort(self),
            'example': ComponentTest.TestPort(self),
            'component': Component(),
            'one': 1,
            'none': None
        }
        self.numberoftestport = len(
            [
                port for port in self.namedports.values()
                if isinstance(port, ComponentTest.TestPort)
            ]
        )
        self.bindcount = self.numberoftestport
        self.unbindcount = self.numberoftestport

    def test_init(self):
        """Test to set ports in the constructor.
        """

        ports = self.namedports.values()
        self.component = Component(ports=ports, namedports=self.namedports)

        self.assertEqual(2 * len(self.namedports), len(self.component))

    def test_generated_id(self):
        """Test generated ids.
        """

        count = 5000

        ids = set()
        for i in range(count):
            ids.add(Component().uid)

        self.assertEqual(len(ids), count)

    def test_id(self):
        """Test specific uid.
        """

        testid = 'test'
        ctest = Component(uid=testid)
        self.assertEqual(ctest.uid, testid)

        exampleid = 'example'
        cexample = Component(uid=exampleid)
        self.assertEqual(cexample.uid, exampleid)

        self.assertNotEqual(cexample.uid, ctest.uid)

    def _testexistingports(self):
        """Test named ports.

        :param init: initialization function.
        """
        self.assertEqual(len(self.component), len(self.namedports))
        for name in self.namedports:
            self.assertTrue(self.component.contains(name))
            self.assertIn(name, self.component)
            port = self.component[name]
            self.assertIs(port, self.namedports[name])

        self.assertEqual(self.bindcount, 0)
        self.assertEqual(self.unbindcount, self.numberoftestport)

    def _initcomponentwithports(self):
        """Fill self component with self ports.
        """

        self.component = Component(namedports=self.namedports)
        self._testexistingports()

    def test_clear(self):
        """Test clear method.
        """

        self._initcomponentwithports()
        self.component.clear()
        self.assertEqual(len(self.component), 0)
        self.assertEqual(self.bindcount, 0)
        self.assertEqual(self.unbindcount, 0)

    def test_setdefault(self):
        """Test setdefault.
        """

        bindcount = self.numberoftestport

        # test setdefault
        for index, name in enumerate(self.namedports):
            port = self.namedports[name]
            p = self.component.setdefault(name, port)
            self.assertIs(port, p)
            if isinstance(port, ComponentTest.TestPort):
                bindcount -= 1
            self.assertEqual(self.bindcount, bindcount)
            self.assertEqual(self.unbindcount, self.numberoftestport)
            p = self.component.setdefault(name, port)
            self.assertIs(port, p)
            self.assertEqual(self.bindcount, bindcount)
            self.assertEqual(self.unbindcount, self.numberoftestport)

    def test_pop(self):
        """Test pop method.
        """

        self._initcomponentwithports()

        self.assertRaises(KeyError, self.component.pop, '')

        poped_value = self.component.pop('', 5)
        self.assertIs(poped_value, 5)

        for name in self.namedports:
            named_port = self.namedports[name]
            port = self.component.pop(name)
            self.assertIs(port, named_port)

        self.assertFalse(self.component)
        # assert to pop something from an empty component
        self.assertRaises(KeyError, self.component.pop, '')
        notexistingport = self.component.pop('', self)
        self.assertIs(notexistingport, self)

    def test_init_ports(self):
        """Test to init ports.
        """

        self._initcomponentwithports()

    def test_update_ports(self):
        """Test to update ports.
        """

        self.component.update(self.namedports)
        self._testexistingports()

    def test_bind_ports(self):
        """Test to bind ports.
        """

        for name in self.namedports:
            port = self.namedports[name]
            self.component[name] = port
        self._testexistingports()

    def test_set_ports(self):
        """Test to set ports.
        """

        for name in self.namedports:
            port = self.namedports[name]
            self.component.setport(port=port, name=name)
        self._testexistingports()

    def test_unbind_port(self):
        """Test to unbind ports.
        """

        self._initcomponentwithports()

        for name in self.namedports:
            self.assertIn(name, self.component)
            del self.component[name]
            self.assertNotIn(name, self.component)

        self.assertEqual(len(self.component), 0)

    def test_remove_port(self):
        """Test to remove ports.
        """

        self._initcomponentwithports()

        for name in self.namedports:
            self.assertTrue(self.component.contains(name))
            self.component.removeport(name)
            self.assertFalse(self.component.contains(name))

        self.assertEqual(len(self.component), 0)

    def test_get_ports_default(self):
        """Test getports method without parameters.
        """

        self._initcomponentwithports()

        ports = self.component.getports()

        self.assertEqual(ports, self.namedports)

    def test_get_ports_name(self):
        """Test getports method with name.
        """

        self._initcomponentwithports()

        for name in self.namedports:
            ports = self.component.getports(names=name)
            self.assertEqual(len(ports), 1)
            self.assertIn(name, ports)

    def test_get_ports_names(self):
        """Test getports method with names.
        """

        self._initcomponentwithports()
        names = self.namedports.keys()[1:]
        ports = self.component.getports(names=names)

        self.assertEqual(len(ports), len(self.namedports) - 1)
        for name in names:
            self.assertIn(name, ports)

    def test_get_ports_regex(self):
        """Test getports method with names such as regex.
        """

        self._initcomponentwithports()
        names = ".*"
        ports = self.component.getports(names=names)

        self.assertEqual(len(ports), len(self.namedports))

    def test_get_ports_list_regex(self):
        """Test getports method with names such as list of regex.
        """

        self._initcomponentwithports()
        full_names = [name for name in list(self.namedports)[:2]]
        names = ["^{0}.*".format(name[:2]) for name in full_names]
        ports = self.component.getports(names=names)

        self.assertEqual(len(ports), 2)
        for name in full_names:
            self.assertIn(name, ports)

    def test_get_ports_type(self):
        """Test getports method with type.
        """

        self._initcomponentwithports()

        _type = ComponentTest.TestPort
        ports = self.component.getports(types=_type)

        self.assertEqual(len(ports), self.numberoftestport)
        for name in ports:
            port = ports[name]
            self.assertTrue(isinstance(port, _type))

    def test_get_ports_types(self):
        """Test getports method with types.
        """

        self._initcomponentwithports()

        types = []

        for name in self.namedports:
            port = self.namedports[name]
            if not isinstance(port, Component):
                types.append(port.__class__)

        self.assertTrue(types)
        ports = self.component.getports(types=types)

        self.assertEqual(len(ports), len(types))

        for name in ports:
            port = ports[name]
            self.assertFalse(isinstance(port, Component))

    def test_get_ports_select(self):
        """Test getports method with a combination of names and types.
        """

        self._initcomponentwithports()

        components_count = len(
            [
                port for port in self.namedports.values()
                if isinstance(port, Component)
            ]
        )

        ports = self.component.getports(
            select=lambda name, port: isinstance(port, Component)
        )

        self.assertEqual(len(ports), components_count)

    def test_delete(self):
        """Test to delete component with delete method.
        """

        self._initcomponentwithports()

        self.component.delete()

        self.assertEqual(len(self.component), 0)
        self.assertEqual(self.unbindcount, 0)

    def test__del__(self):
        """Test to delete component with __del__ method.
        """

        self._initcomponentwithports()

        self.component.__del__()

        self.assertEqual(len(self.component), 0)
        self.assertEqual(self.unbindcount, 0)

    def test_del(self):
        """Test to delete component with del operator.
        """

        self._initcomponentwithports()

        del self.component

        self.assertEqual(self.unbindcount, 0)

    def test_contains_str(self):
        """Test contains method with a str.
        """

        names = 'test', 'example'
        value = 'testcase'

        self.component[names[0]] = None
        self.component[names[1]] = value

        self.assertTrue(self.component.contains(names[0]))
        self.assertFalse(self.component.contains('not existing'))
        self.assertTrue(self.component.contains(names[1]))
        self.assertTrue(self.component.contains(value))

    def test__contains__str(self):
        """Test __contains__ method with a str.
        """

        names = 'test', 'example'
        value = 'testcase'

        self.component[names[0]] = None
        self.component[names[1]] = value

        self.assertIn(names[0], self.component)
        self.assertNotIn('not existing', self.component)
        self.assertIn(names[1], self.component)
        self.assertIn(value, self.component)

    def test_contains(self):
        """Test contains method with an object.
        """

        name = 'test'
        values = None, Component(), 2

        for value in values:
            self.component[name] = value
            self.assertTrue(self.component.contains(value))

    def test__contains__(self):
        """Test __contains__ method with an object.
        """

        name = 'test'
        values = None, Component(), 2

        for value in values:
            self.component[name] = value
            self.assertIn(value, self.component)

    def test_get_cls_ports_default(self):
        """Test get_cls_ports method without parameters.
        """

        self._initcomponentwithports()

        ports = Component.GETPORTS(self.component)

        component_ports = {}
        for name in self.namedports:
            port = self.namedports[name]
            if isinstance(port, Component):
                component_ports[name] = port

        self.assertEqual(ports, component_ports)

    def test_get_cls_ports_name(self):
        """Test get_cls_ports method with name.
        """

        self._initcomponentwithports()

        for name in self.namedports:
            port = self.namedports[name]
            if isinstance(port, Component):
                ports = Component.GETPORTS(self.component, names=name)
                self.assertEqual(len(ports), 1)
                self.assertIn(name, ports)

    def test_get_cls_ports_names(self):
        """Test get_cls_ports method with names.
        """

        self._initcomponentwithports()
        names = [
            name for name in self.namedports
            if isinstance(self.namedports[name], Component)
        ]
        ports = Component.GETPORTS(self.component, names=names)

        self.assertEqual(len(ports), len(names))
        for name in names:
            self.assertIn(name, ports)

    def test_get_cls_ports_type(self):
        """Test get_cls_ports method with type.
        """

        self._initcomponentwithports()

        ports = ComponentTest.TestPort.GETPORTS(self.component)

        self.assertEqual(len(ports), self.numberoftestport)
        for name in ports:
            port = ports[name]
            self.assertTrue(isinstance(port, ComponentTest.TestPort))

    def test_get_cls_ports_select(self):
        """Test get_cls_ports method with a combination of names and types.
        """

        self._initcomponentwithports()

        components_count = len(
            [
                port for port in self.namedports.values()
                if isinstance(port, Component)
            ]
        )

        ports = Component.GETPORTS(
            self.component,
            select=lambda name, port: isinstance(port, Component)
        )

        self.assertEqual(len(ports), components_count)

    def test_generated_name(self):
        """Test to set a port with a generated name.
        """

        port = 'test'

        generated_name, _ = self.component.setport(port=port)

        self.assertIs(self.component[generated_name], port)


if __name__ == '__main__':
    main()
