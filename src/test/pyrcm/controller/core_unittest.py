import unittest

from pyrcm.core import Component
from pyrcm.controller.core import ComponentController
from pyrcm.membrane.core import ComponentMembrane


class TestController(ComponentController):
    pass


class controllerTest(unittest.TestCase):

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
    unittest.main()
