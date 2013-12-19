import unittest

from pyrcm.core import Component
from pyrcm.controller.core import Controller


class TestController(Controller):
    pass


class controllerTest(unittest.TestCase):

    def testComponent(self):

        component = Component()
        controller = TestController(component)

        _controller = TestController.GET_CONTROLLER(component)

        self.assertEquals(controller, _controller)
        self.assertEquals(controller.get_component(), component)

if __name__ == '__main__':
    unittest.main()
