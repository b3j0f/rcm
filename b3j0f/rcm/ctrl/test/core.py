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

        def _onbind(self, *args, **kwargs):

            super(ControllerTest.TestController, self)._onbind(*args, **kwargs)

            self.controllertest.bindcount += 1

        def _onunbind(self, *args, **kwargs):

            super(ControllerTest.TestController, self)._onunbind(
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
        """Test Controller.getctrl static method.
        """

        # bind controllers to components
        for component in self.components:
            Controller.bindall(component, *self.controllers)

        for controller in self.controllers:
            for component in self.components:
                # assert with existing controller
                _controller = controller.__class__.getctrl(component)
                self.assertIs(_controller, controller)
                # assert controller is missing after unbind it from component
                del component[controller.ctrlname()]
                _controller = controller.__class__.getctrl(component)
                self.assertIsNone(_controller)
                # assert with not existing controller
                _controller = ControllerTest.NotController.getctrl(
                    component
                )
                self.assertIsNone(_controller)

    def test_bind_to_component(self):
        """Test bindto class method on one component at a time.
        """

        for component in self.components:
            ControllerTest.TestController.bindto(component, self)
            ControllerTest.TestSlotsController.bindto(component, self)
            controllers = Controller.GETPORTS(component)
            self.assertEqual(len(controllers), len(self.controllers))

        self.assertEqual(
            self.bindcount, 2 * len(self.components)
        )
        self.assertEqual(self.unbindcount, 0)

    def test_bind_to_components(self):
        """Test bindto class method on components.
        """

        ControllerTest.TestController.bindto(self.components, self)
        ControllerTest.TestSlotsController.bindto(self.components, self)

        self.assertEqual(
            self.bindcount, 2 * len(self.components)
        )
        self.assertEqual(self.unbindcount, 0)

    def test_unbind_from_component(self):
        """Test unbindfrom class method on one component at a time.
        """

        # bind controllers
        self.test_bind_to_components()

        for component in self.components:
            ControllerTest.TestController.unbindfrom(component)
            ControllerTest.TestSlotsController.unbindfrom(component)
            controllers = Controller.GETPORTS(component)
            self.assertEqual(len(controllers), 0)

        self.assertEqual(self.unbindcount, 2 * len(self.components))

    def test_unbind_from_components(self):
        """Test unbindfrom class method on components.
        """

        # bind controllers
        self.test_bind_to_components()

        ControllerTest.TestController.unbindfrom(*self.components)
        ControllerTest.TestSlotsController.unbindfrom(*self.components)

        self.assertEqual(self.unbindcount, 2 * len(self.components))

    def test_bind_all(self):
        """Test bind to static method.
        """

        # bind controllers to components
        for component in self.components:
            controllers = Controller.GETPORTS(component)
            self.assertFalse(controllers)
            Controller.bindall(component, *self.controllers)
            controllers = Controller.GETPORTS(component)
            self.assertEqual(len(controllers), len(self.controllers))

        self.assertEqual(
            self.bindcount, len(self.controllers) * len(self.components)
        )

    def test_unbind_all(self):
        """Test unbind from static method.
        """

        # unbind controllers from components
        for component in self.components:
            Controller.bindall(component, *self.controllers)
            controllers = Controller.GETPORTS(component)
            self.assertEqual(len(controllers), len(self.controllers))
            Controller.unbindall(component, *self.controllers)
            controllers = Controller.GETPORTS(component)
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
            Controller.bindall(component, *self.controllers)

        for controller in self.controllers:
            controller.delete()
            self.assertFalse(controller._boundon)

        self.assertEqual(
            self.bindcount, len(self.components) * len(self.controllers)
        )
        self.assertEqual(
            self.unbindcount, len(self.components) * len(self.controllers)
        )

if __name__ == '__main__':
    main()
