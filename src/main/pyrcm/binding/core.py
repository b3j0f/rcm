from pyrcm.core import Component


class Binding(Component):
    """
    Component binding related to an interface.
    """

    def __init__(self, name=None, interface=None):

        super(Binding, self).__init__(interface=interface)
        self.name = name


class Interface(Component):
    """
    Component interface which manages bindings. It is a server or a client.
    """

    def __init__(self, component, is_server):

        super(Interface, self).__init__(component=component)
        self._is_server = is_server

    @Service()
    def is_server(self):
        """
        True if this is a server interface.
        """

        return self._is_server

    def start(self):
        """
        Start all bindings.
        """

        for name, binding in enumerate(self):
            if name != 'component':
                binding.start()

    def stop(self):
        """
        Stop all bindings.
        """

        for name, binding in enumerate(self):
            if name != 'component':
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
