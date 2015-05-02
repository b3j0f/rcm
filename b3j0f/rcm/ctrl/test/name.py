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
from b3j0f.rcm.ctrl.core import Controller
from b3j0f.rcm.ctrl.name import (
    NameController, GetName, SetName
)
from b3j0f.rcm.ctrl.impl import ImplController


class Business(object):

    @GetName()
    def get_name(self):
        return self.name if hasattr(self, 'name') else type(self).__name__

    @SetName()
    def set_name(self, name):
        self.name = name


class NameTest(UTCase):

    def setUp(self):
        self.name = 'NameTest'
        self.component = Component()
        self.controller = NameController(name=self.name)
        self.implController = ImplController()
        Controller.bind_to(
            self.component, self.controller, self.implController
        )

    def testNameController(self):

        self.assertEquals(self.controller.name, self.name)
        self.assertEquals(NameController.get_name(self.component), self.name)

        self.name += self.name

        self.controller.name = self.name

        self.assertEquals(self.controller.name, self.name)
        self.assertEquals(NameController.get_name(self.component), self.name)

    def testContextName(self):

        self.assertEquals(self.name, self.controller.name)

        ImplController.update_impl(self.component, Business)
        self.assertEquals(Business.__name__, self.controller.name)

        self.controller.set_name(self.name)
        self.assertEquals(self.name, self.controller.name)
        self.assertEquals(
            self.component.get_implementation().name,
            self.controller.name
        )

if __name__ == '__main__':
    main()
