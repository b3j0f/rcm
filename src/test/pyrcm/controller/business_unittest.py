import unittest

from pyrcm.core import Component
from pyrcm.controller.business import BusinessController


class Business(object):

    @Context
    def set_component(self, component):
        self.component = component

    def get_component(self):



class testBusiness(unittest.TestCase):

    def testContext(self):
        pass

    def testRenew(self):
        pass

    pass

if __name__ == '__main__':
    unittest.main()
