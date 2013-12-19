from pyrcm.core import Component
from pyrcm.controller.name import NameController

import unittest


class NameTest(unittest.TestCase):

    def testName(self):

        name = 'NameTest'

        component = Component()
        controller = NameController(component, name)
        ScopeController(component)

        self.assertEquals(controller.get_name(), name)
        self.assertEquals(NameController.GET_NAME(component), name)

        name += name

        controller.set_name(name)

        self.assertEquals(controller.get_name(), name)
        self.assertEquals(NameController.GET_NAME(component), name)

if __name__ == '__main__':
    unittest.main()
