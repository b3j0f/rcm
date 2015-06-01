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


class Business(object):

    @SetNameCtrl()
    def set_name_ctrl(self, namectrl):
        """Set NameController.
        """

        self.namectrl = namectrl

    @GetName()
    def get_name(self):
        """Get controller name.
        """

        return self.name if hasattr(self, 'name') else type(self).__name__

    @SetName()
    def set_name(self, name):
        """Change of controller name.
        """

        self.name = name


class NameControllerTest(UTCase):

    def setUp(self):
        self.name = 'NameTest'
        self.component = Component()
        self.controller = NameController(name=self.name)
        self.controller.apply(self.component)

    def testNameController(self):

        self.assertEquals(self.controller.name, self.name)
        self.assertEquals(NameController.GET_NAME(self.component), self.name)

        name = '{0}{0}'.format(self.name)

        self.controller.name = name

        self.assertEquals(self.controller.name, name)
        self.assertEquals(NameController.GET_NAME(self.component), name)
        print 'ok', self.name
        NameController.SET_NAME(name=self.name, component=self.component)
        self.assertEquals(self.controller.name, self.name)
        self.assertEquals(NameController.GET_NAME(self.component), self.name)


class GetUname(NameControllerTest):

    def test(self):

        uname = "{0}-{1}".format(self.controller.name, self.component.uid)
        UNAME = NameController.GET_UNAME(component=self.component)
        self.assertEqual(uname, UNAME)


if __name__ == '__main__':
    main()
