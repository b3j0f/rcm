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
from b3j0f.rcm.ctrl.name import (
    NameController, GetName, SetName, SetNameCtrl
)


class AnnotationTest(UTCase):
    """Test annotations.
    """

    class Business(object):
        """Default implementation with annotations IoC/ID mechanisms.
        """

        @SetNameCtrl()
        def set_name_nf(self, namenf):
            """Set NameController.

            :param NameController namenf: component NameController.
            """

            self.namenf = namenf

        @GetName()
        def get_name(self):
            """Get controller name.

            :return: component name.
            :rtype: str
            """

            return getattr(self, 'name', type(self).__name__)

        @SetName()
        def set_name(self, name):
            """Change of controller name.

            :param str name: new controller name.
            """

            self.name = name


class BaseNameControllerTest(UTCase):
    """Base class for all NameController tests which instantiates a component
    and a NameController.
    """
    def setUp(self):

        self.name = 'NameTest'
        self.component = Component()
        self.controller = NameController(name=self.name)
        self.controller.apply(self.component)


class NameTest(BaseNameControllerTest):
    """Test for set/get controller name.
    """

    def test_name(self):
        """Test getter/setter controller.name.
        """

        self.assertEquals(self.controller.name, self.name)
        name = '{0}{0}'.format(self.name)
        self.controller.name = name
        self.assertEquals(self.controller.name, name)

    def test_GET_NAME(self):
        """Test GET_NAME method.
        """

        self.assertEquals(NameController.GET_NAME(self.component), self.name)

        # change of controller name
        name = '{0}{0}'.format(self.name)
        self.controller.name = name
        self.assertEquals(self.controller.name, name)
        self.assertEquals(NameController.GET_NAME(self.component), name)

    def test_SET_NAME(self):
        """Test SET_NAME method.
        """

        NameController.SET_NAME(name=self.name, component=self.component)
        self.assertEquals(self.controller.name, self.name)
        self.assertEquals(NameController.GET_NAME(self.component), self.name)


class GET_UNAMETest(BaseNameControllerTest):
    """Test GET_UNAME method.
    """

    def test(self):

        uname = "{0}-{1}".format(self.controller.name, self.component.uid)
        UNAME = NameController.GET_UNAME(component=self.component)
        self.assertEqual(uname, UNAME)


class GET_PORTS_BY_NAMETest(BaseNameControllerTest):
    """Test GET_PORTS_BY_NAME method.
    """

    def setUp(self):

        super(GET_PORTS_BY_NAMETest, self).setUp()

        # prepare count components with NameController
        self.count = 5
        self.names = [str(i) for i in range(self.count)]
        for name in self.names:
            component = Component()
            self.component.set_port(port=component)
            controller = NameController(name=name)
            controller.apply(component)

    def test_names(self):
        """Test with names.
        """

        ports = NameController.GET_PORTS_BY_NAME(
            self.component, *self.names
        )
        ports = [NameController.GET_NAME(port) for port in ports.values()]
        self.assertEqual(set(ports), set(self.names))

    def test_name(self):
        """Test with one name.
        """

        ports = NameController.GET_PORTS_BY_NAME(
            self.component, self.names[0]
        )
        self.assertEqual(len(ports), 1)
        self.assertEqual(
            NameController.GET_NAME(ports.values()[0]),
            self.names[0]
        )

    def test_no_name(self):
        """Test with no name.
        """

        ports = NameController.GET_PORTS_BY_NAME(
            self.component
        )
        self.assertFalse(ports)


class GET_PORTTest(BaseNameControllerTest):
    """Test GET_PORT method.
    """


if __name__ == '__main__':
    main()
