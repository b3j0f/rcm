import unittest

from pyrcm.core import Component
from pyrcm.controller.core import Controller


class TestController(Controller):
    pass


class controllerTest(unittest.TestCase):

    def setUp(self):
        self.component = Component()
        self.controller = TestController(self.component)

    def testComponent(self):

        _controller = TestController.GET_CONTROLLER(self.component)

        self.assertEquals(self.controller, _controller)
        component = self.controller.get_component()
        self.assertTrue(component is self.component)

    def testInterfaces(self):

        interfaces = self.component.get_interfaces()
        self.assertEquals(len(interfaces), 0)

        interfaces = self.component.get_interfaces(include_controllers=True)
        self.assertEquals(len(interfaces), 1)

    def testUnicity(self):

        controller2 = TestController(self.component)

        interfaces = self.component.get_interfaces()
        self.assertEquals(len(interfaces), 0)

        interfaces = self.component.get_interfaces(include_controllers=True)

        self.assertEquals(len(interfaces), 1)
        self.assertTrue(interfaces.values()[0] is controller2)

if __name__ == '__main__':
    unittest.main()
