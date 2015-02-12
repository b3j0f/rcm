import unittest

from pyrcm.core import Component
from pyrcm.membrane.core import ComponentMembrane, Membrane, ComponentBusiness


class MembraneTest(unittest.TestCase):

    def setUp(self):
        self.component = Component()
        self.membrane = ComponentMembrane(self.component)

    def testMembrane(self):

        class Impl(object):
            @Membrane
            def set_membrane(self, membrane):
                self.membrane = membrane

            def get_membrane(self):
                return self.membrane

        self.component.renew_implementation(Impl)

        membrane = ComponentMembrane.GET_MEMBRANE(self.component)
        self.assertTrue(
            self.component.get_membrane() is membrane)

    def testComponentBusiness(self):

        @ComponentBusiness()
        class Impl(object):
            pass

if __name__ == '__main__':
    unittest.main()
