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
from b3j0f.rcm.controller.core import ComponentController
from b3j0f.rcm.membrane.core import ComponentMembrane


class TestController(ComponentController):
    pass


class controllerTest(UTCase):

    def setUp(self):
        self.component = Component()
        self.membrane = ComponentMembrane(self.component)
        self.controller = TestController(self.membrane)

    def testComponent(self):

        _controller = TestController.GET_CONTROLLER(self.component)

        self.assertEquals(self.controller, _controller)
        component = self.controller.get_membrane().get_business_component()
        self.assertTrue(component is self.component)

    def testInterfaces(self):

        interfaces = self.component.get_interfaces()
        self.assertEquals(len(interfaces), 1)

        interfaces = self.membrane.get_interfaces()
        self.assertEquals(len(interfaces), 2)

        interfaces = self.controller.get_interfaces()
        self.assertEquals(len(interfaces), 1)

if __name__ == '__main__':
    main()
