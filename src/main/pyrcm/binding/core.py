from pyrcm.core import Component


class Interface(Component):
    """
    Component interface which manages bindings.\
    It is a server (default) or a client.
    """

    def __init__(
        self, component, name=None, interface_type=None, is_service=True
    ):

        super(Interface, self).__init__(component=component)
        self.is_service(is_service)
        self.set_interface_type(interface_type)
        self.set_name(name)
        component.set_interface(interface=self, name=self.get_name())

    def is_service(self, is_service=None):
        """
        True if this is a service interface.
        """

        if is_service is not None:
            self._is_service = is_service

        return self._is_service

    def get_component(self):
        """
        Get this component.
        """

        return self[Component.NAME]

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

    def get_interface_type(self):
        """
        Get this interface_type.
        """

        return self._interface_type

    def set_interface_type(self, interface_type):
        """
        Change of interface_type and returns the previous one.
        """

        result = getattr(self, '_interface_type', None)

        self._interface_type = interface_type

        return result

    def get_name(self):
        """
        Get this name.
        """

        return self._name

    def set_name(self, name):
        """
        Change of name and returns the previous one.
        """

        result = getattr(self, '_name', None)

        if name is None:
            service_type = self.get_service_type()
            if service_type is not None:
                name = Component.GENERATE_INTERFACE_NAME(self)
            else:
                name = Component.GENERATE_INTERFACE_NAME(service_type)

        self._name = name

        return result

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

    def __init__(self, name=None, interface=None):

        super(Binding, self).__init__(interface=interface)
        self.name = name
