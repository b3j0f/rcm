"""
Contains all core objects related to a reflective component model.
"""


class Component(dict):
    """
    Component which contains Interfaces.
    """

    NAME = 'component'

    def __init__(self, **named_interfaces):

        self.update(named_interfaces)

    def __getitem__(self, key):
        """
        Get the interface which has the input key.
        If no interface exist, a NoSuchInterfaceError is raised.
        """
        result = super(Component, self).__getitem__(key)

        return result

    def __setitem__(self, key, interface):
        """
        Change the named interface designated by the input key \
        with the input interface and returns the old one if it exists.
        """

        result = self.get(key, None)

        super(Component, self).__setitem__(key, interface)

        return result

    def start(self):
        """
        Start this component and all interfaces which are components.
        """

        for interface in self.values():
            if isinstance(interface, Component):
                interface.start()

    def stop(self):
        """
        Stop this component and all interfaces which are components.
        """

        for interface in self.values():
            if isinstance(interface, Component):
                interface.stop()


class Interface(Component):
    """
    Component interface which manages bindings.
    """

    def __init__(self, component, bindings=[]):

        super(Interface, self).__init__(component=component)
        self.bindings = bindings

    def get_bindings(self):
        """
        Return this bindings.
        """
        return self.bindings

    def start(self):
        """
        Start all bindings.
        """

        for binding in self.bindings:
            binding.start()

    def stop(self):
        """
        Stop all bindings.
        """

        for binding in self.bindings:
            binding.stop()

    @staticmethod
    def GET_BINDINGS(component, interface_name):
        """
        Get all component bindings related to the input interface name.
        """

        result = []

        interface = component.get(interface_name, None)

        if isinstance(interface, Interface):
            result = interface.get_bindings()

        return result


class Binding(Component):
    """
    Component binding related to an interface.
    """

    def __init__(self, interface):

        super(Binding, self).__init__(interface=interface)
