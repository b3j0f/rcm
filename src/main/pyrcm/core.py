"""
Contains definition of Component.
"""
from pycoann.core import Decorator
from pyrcm.binding import Service, Reference


class Component(Decorator, dict):
    """
    Component which contains Interfaces.
    Can be used such as a decorator in order to specialize a component \
    business class.
    """

    NAME = 'component'

    def __init__(self, *controllers, **interfaces):

        self.update(interfaces)
        for controller in controllers:
            self.set_interface(controller)

    @Service()
    def get_interface(self, interface_name):

        return self[interface_name]

    @Reference()
    def set_interface(self, interface, name=None):

        if name is None:
            interface_type = type(interface)
            name = "%s.%s" % \
                (interface_type.__module__, interface_type.__name__)

        self[name] = interface

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

    @Service()
    def start(self):
        """
        Start this component. Do nothing by default.
        """

        pass

    @Service()
    def stop(self):
        """
        Stop this component. Do nothing by default.
        """

        pass
