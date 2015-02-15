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
from b3j0f.rcm.controller.core import Controller


class ControllerTest(UTCase):
    """Test Controller methods.
    """

    class TestController(Controller):
        """Controller test class.
        """
        pass

    class TestSlotsController(Controller):
        """Controller test class with slots.
        """
        __slots__ = Controller.__slots__

    def setUp(self):
        """Initialize tests with one component and both test controllers.
        """
        self.components = Component(), Component()
        self.controllers = (
            ControllerTest.TestController(),
            ControllerTest.TestSlotsController()
        )
        # bind controllers to components
        for component in self.components:
            Controller.bind_to(component, *self.controllers)

    def test_get_controller(self):
        """Test Controller.get_controller static method.
        """

        for controller in self.controllers:
            for component in self.components:
                _controller = controller.__class__.get_controller(component)
                self.assertIs(_controller, controller)

                _controller = controller.__class__.get_controller(component)
                self.assertIs(_controller, controller)


if __name__ == '__main__':
    main()
