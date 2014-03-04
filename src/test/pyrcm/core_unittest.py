import unittest

from pyrcm.core import Component


class CoreTest(unittest.TestCase):

    def setUp(self):
        self.component = Component()

    def test_generate_name(self):
        s = set()

        count = 1000

        xr = xrange(count)

        for i in xr:
            generated_name =\
                Component.GENERATE_INTERFACE_NAME(
                    interface=CoreTest, generated=True)
            s.add(generated_name)

        self.assertEquals(len(s), count)

    def test_interfaces(self):

        interfaces = self.component.get_interfaces()
        self.assertEquals(len(interfaces), 0)
        self.assertEquals(len(self.component), 0)

        component = Component(None, None)
        interfaces = component.get_interfaces()

        self.assertEquals(len(component), 2)
        self.assertEquals(len(interfaces), 2)

        component = Component(a=None, b=None)
        interfaces = component.get_interfaces()

        self.assertEquals(len(component), 2)
        self.assertEquals(len(interfaces), 2)

        component = Component(1, None, a=None, b=1)
        interfaces = component.get_interfaces()

        self.assertEquals(len(component), 4)
        self.assertEquals(len(interfaces), 4)

        self.assertTrue(component.has_interface('a'))
        self.assertTrue(component.has_interface('b'))
        self.assertFalse(component.has_interface('c'))

        for name in interfaces:
            has_interface = component.has_interface(name)
            self.assertTrue(has_interface)

        for name in component:
            has_interface = component.has_interface(name)
            self.assertTrue(has_interface)

        interfaces = component.get_interfaces(int)

        self.assertEquals(len(interfaces), 2)

        interfaces = component.get_interfaces(type(None))

        self.assertEquals(len(interfaces), 2)

        interfaces = component.get_interfaces((int,))

        self.assertEquals(len(interfaces), 2)

        interfaces_names = component.get_interface_names(None)

        self.assertEquals(len(interfaces_names), 2)

    def test_set_interface(self):

        self.component.set_interface(None)

        self.assertEquals(len(self.component), 1)

        self.component[None] = None

        self.assertEquals(len(self.component), 2)

        a = 'a'

        self.component.set_interface(None, name=a)

        has_interface = self.component.has_interface(a)
        self.assertTrue(has_interface)
        self.assertEquals(len(self.component), 3)

        self.component[a] = None

        has_interface = self.component.has_interface(a)
        self.assertTrue(has_interface)
        self.assertEquals(len(self.component), 3)

    def test_remove_interface(self):

        a = 'a'
        b = 'b'
        self.component[a] = a
        self.component[b] = b

        has_interface_a = self.component.has_interface(a)
        self.assertTrue(has_interface_a)
        self.assertEquals(len(self.component), 2)

        ra = self.component.remove_interface(name=a)

        has_interface_a = self.component.has_interface(a)
        self.assertFalse(has_interface_a)
        self.assertEquals(len(self.component), 1)
        self.assertTrue(ra is a)

        del self.component[b]

        has_interface_b = self.component.has_interface(b)
        self.assertFalse(has_interface_b)
        self.assertEquals(len(self.component), 0)

    def test_implementation(self):

        implementation = self.component.get_implementation()
        self.assertTrue(implementation is self.component)

        class ImplA(object):
            def __init__(self, a=None):
                self.a = a

            def get_a(self):
                return self.a

            from pyrcm.core import Context

            @Context
            def set_context(self, context):
                self.context = context

            def get_context(self):
                return self.context

        class ImplB(object):
            def __init__(self):
                pass

            def get_b(self):
                pass

        impl = ImplA()
        self.component.set_implementation(impl)
        implementation = self.component.get_implementation()
        self.assertTrue(implementation is impl)
        self.assertTrue(implementation.get_context() is self.component)
        self.assertTrue(hasattr(self.component, 'get_a'))

        self.component.set_implementation(impl)
        implementation = self.component.get_implementation()
        self.assertTrue(implementation is impl)
        self.assertTrue(hasattr(self.component, 'get_a'))

        impl = ImplB()
        self.component.set_implementation(impl)
        implementation = self.component.get_implementation()
        self.assertTrue(implementation is impl)
        self.assertFalse(hasattr(self.component, 'get_a'))
        self.assertTrue(hasattr(self.component, 'get_b'))

        impl = self.component.renew_implementation(ImplA)

        self.assertTrue(type(impl) is ImplA)
        implementation = self.component.get_implementation()
        self.assertTrue(implementation is impl)
        self.assertFalse(hasattr(self.component, 'get_b'))
        self.assertTrue(hasattr(self.component, 'get_a'))

        impl = self.component.renew_implementation(
            ImplA, a=1)
        self.assertTrue(type(impl) is ImplA)
        implementation = self.component.get_implementation()
        self.assertTrue(implementation is impl)
        self.assertTrue(hasattr(self.component, 'get_a'))
        a = self.component.get_a()
        self.assertTrue(a is 1)

if __name__ == '__main__':
    unittest.main()
