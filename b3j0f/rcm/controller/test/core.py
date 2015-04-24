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

        def __init__(self, controllertest, *args, **kwargs):

            super(ControllerTest.TestController, self).__init__(
                *args, **kwargs
            )

            self.controllertest = controllertest

        def _on_bind(self, *args, **kwargs):

            super(ControllerTest.TestController, self)._on_bind(*args, **kwargs)

            self.controllertest.bindcount += 1

        def _on_unbind(self, *args, **kwargs):

            super(ControllerTest.TestController, self)._on_unbind(
                *args, **kwargs
            )

            self.controllertest.unbindcount += 1

    class TestSlotsController(TestController):
        """Controller test class with slots.
        """

    class NotController(Controller):
        """Controller test class which won't be added to the tests.
        """

    def setUp(self):
        """Initialize tests with one component and both test controllers.
        """
        self.bindcount = 0
        self.unbindcount = 0
        self.components = Component(), Component()
        self.controllers = (
            ControllerTest.TestController(self),
            ControllerTest.TestSlotsController(self)
        )

    def test_get_controller(self):
        """Test Controller.get_controller static method.
        """

        # bind controllers to components
        for component in self.components:
            Controller.bind_all(component, *self.controllers)

        for controller in self.controllers:
            for component in self.components:
                # assert with existing controller
                _controller = controller.__class__.get_controller(component)
                self.assertIs(_controller, controller)
                # assert controller is missing after unbind it from component
                del component[controller.ctrl_name()]
                _controller = controller.__class__.get_controller(component)
                self.assertIsNone(_controller)
                # assert with not existing controller
                _controller = ControllerTest.NotController.get_controller(
                    component
                )
                self.assertIsNone(_controller)

    def test_bind_to_component(self):
        """Test bind_to class method on one component at a time.
        """

        for component in self.components:
            ControllerTest.TestController.bind_to(component, self)
            ControllerTest.TestSlotsController.bind_to(component, self)
            controllers = Controller.GET_PORTS(component)
            self.assertEqual(len(controllers), len(self.controllers))

        self.assertEqual(
            self.bindcount, 2 * len(self.components)
        )
        self.assertEqual(self.unbindcount, 0)

    def test_bind_to_components(self):
        """Test bind_to class method on components.
        """

        ControllerTest.TestController.bind_to(self.components, self)
        ControllerTest.TestSlotsController.bind_to(self.components, self)

        self.assertEqual(
            self.bindcount, 2 * len(self.components)
        )
        self.assertEqual(self.unbindcount, 0)

    def test_unbind_from_component(self):
        """Test unbind_from class method on one component at a time.
        """

        # bind controllers
        self.test_bind_to_components()

        for component in self.components:
            ControllerTest.TestController.unbind_from(component)
            ControllerTest.TestSlotsController.unbind_from(component)
            controllers = Controller.GET_PORTS(component)
            self.assertEqual(len(controllers), 0)

        self.assertEqual(self.unbindcount, 2 * len(self.components))

    def test_unbind_from_components(self):
        """Test unbind_from class method on components.
        """

        # bind controllers
        self.test_bind_to_components()

        ControllerTest.TestController.unbind_from(*self.components)
        ControllerTest.TestSlotsController.unbind_from(*self.components)

        self.assertEqual(self.unbindcount, 2 * len(self.components))

    def test_bind_all(self):
        """Test bind to static method.
        """

        # bind controllers to components
        for component in self.components:
            controllers = Controller.GET_PORTS(component)
            self.assertFalse(controllers)
            Controller.bind_all(component, *self.controllers)
            controllers = Controller.GET_PORTS(component)
            self.assertEqual(len(controllers), len(self.controllers))

        self.assertEqual(
            self.bindcount, len(self.controllers) * len(self.components)
        )

    def test_unbind_all(self):
        """Test unbind from static method.
        """

        # unbind controllers from components
        for component in self.components:
            Controller.bind_all(component, *self.controllers)
            controllers = Controller.GET_PORTS(component)
            self.assertEqual(len(controllers), len(self.controllers))
            Controller.unbind_all(component, *self.controllers)
            controllers = Controller.GET_PORTS(component)
            self.assertFalse(controllers)

        self.assertEqual(
            self.bindcount, len(self.controllers) * len(self.components)
        )

        self.assertEqual(
            self.unbindcount, len(self.controllers) * len(self.components)
        )

    def test_del(self):
        """Test del.
        """

        for component in self.components:
            Controller.bind_all(component, *self.controllers)

        for controller in self.controllers:
            controller.delete()
            self.assertFalse(controller._bound_on)

        self.assertEqual(
            self.bindcount, len(self.components) * len(self.controllers)
        )
        self.assertEqual(
            self.unbindcount, len(self.components) * len(self.controllers)
        )

if __name__ == '__main__':
    main()
