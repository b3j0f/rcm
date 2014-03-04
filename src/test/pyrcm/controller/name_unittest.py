import unittest
from pyrcm.core import Component
from pyrcm.membrane.core import ComponentMembrane
from pyrcm.controller.name import NameController, ComponentName


class Business(object):

    @ComponentName
    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name if hasattr(self, 'name') else type(self).__name__


class NameTest(unittest.TestCase):

    def setUp(self):
        self.name = 'NameTest'
        self.component = Component()
        self.membrane = ComponentMembrane(self.component)
        self.controller = NameController(membrane=self.membrane, name=self.name)

    def testNameController(self):

        self.assertEquals(self.controller.get_name(), self.name)
        self.assertEquals(NameController.GET_NAME(self.component), self.name)

        self.name += self.name

        self.controller.set_name(self.name)

        self.assertEquals(self.controller.get_name(), self.name)
        self.assertEquals(NameController.GET_NAME(self.component), self.name)

    def testContextName(self):

        self.component.renew_implementation(Business)
        self.assertEquals(self.name, self.controller.get_name())
        self.assertEquals(self.controller.get_name(), Business.__name__)

if __name__ == '__main__':
    unittest.main()
