import unittest

from pyrcm.core import Component


class CoreTest(unittest.TestCase):

    def testGenerateName(self):
        s = set()

        count = 1000

        xr = xrange(count)

        for i in xr:
            generated_name =\
                Component.GENERATE_INTERFACE_NAME(
                    interface=CoreTest, generated=True)
            s.add(generated_name)

        self.assertEquals(len(s), count)

    def testInterfaces(self):

        component = Component()

        self.assertEquals(len(component), 0)

        component = Component(component, component)

        self.assertEquals(len(component), 2)

        component = Component(a=component, b=component)

        self.assertEquals(len(component), 2)

        component = Component(component, component, a=component, b=component)

        self.assertEquals(len(component), 4)

        self.assertTrue(component.has_interface('a'))
        self.assertTrue(component.has_interface('b'))
        self.assertFalse(component.has_interface('c'))

        for name in component:
            self.assertTrue(component.has_interface(name))

        component.remove_interface('a')

        self.assertFalse(component.has_interface('a'))

        interfaces = component.get_interfaces()

        self.assertEquals(len(interfaces), 3)

    def testSetInterface(self):
        pass

if __name__ == '__main__':
    unittest.main()
