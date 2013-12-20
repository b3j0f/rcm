"""
Contains Component definition.
"""
from uuid import uuid1 as uuid
import inspect


class Component(dict):
    """
    Component which contains Interfaces.
    Can be used such as:\
* a decorator in order to specialize a component business class.\
* a dictionary of interfaces by name.
    """

    class NoSuchInterfaceError(Exception):
        """
        Exception dedicated to component missing interface.
        """

        def __init__(self, component, name=None, component_type=None):
            message =\
                Component.NoSuchInterfaceError._GET_MESSAGE(component, name)
            super(Component.NoSuchInterfaceError, self).__init__(message)

        @staticmethod
        def _GET_MESSAGE(component, name, component_type):
            """
            Get default message for missing interface name in component.
            """

            postfix = \
                "named {0}".format(name) if name is not None \
                else "of type {0}".format(component_type)
            result = "{0} has no interface {1}".format(component, postfix)

            return result

    NAME = 'component'

    def __init__(self, *interfaces, **named_interfaces):
        """
        Constructor which register interfaces with generated name \
and named interfaces.
        """

        # register interface with a generated name.
        for interface in interfaces:
            self.set_interface(interface=interface)

        # register interfaces
        for name, interface in named_interfaces.iteritems():
            self.set_interface(name=name, interface=interface)

    def get_interface(self, name=None, interface_type=None):
        """
        Get interface registered with the input name or the first which \
inherits from input interface_type.\
Raises NoSuchInterfaceError if interface name or interface_type does not exist.
        """

        result = None

        if name is None:
            for interface in self.values():
                if isinstance(interface, interface_type):
                    result = interface
                    break
            if result is None:
                raise Component.NoSuchInterfaceError(
                    self,
                    component_type=interface_type)

        elif name not in self:
            raise Component.NoSuchInterfaceError(self, name=name)

        else:
            result = self[name]

        return result

    def get_interfaces(self, interface_type=None, include_controllers=False):
        """
        Get interface names.
        """

        result = []

        for name, interface in self.iteritems():
            if interface_type is not None and \
                    isinstance(interface, interface_type):
                result.append(name)
            elif include_controllers and isinstance(interface, Controller):
                result.append(name)
            else:
                result.append(name)

        return result

    def get_interface_names(self, interface):
        """
        Get input component interface name.
        Raises NoSuchInterfaceError if interface does not exists.
        """

        result = []

        for interface_name, component_interface in self.iteritems():
            if component_interface is interface:
                result.append(interface_name)

        return result

    def has_interface(self, name):
        """
        Check if interface exists in this component.
        """

        result = name in self

        return result

    def set_interface(self, interface, name=None):
        """
        Set an interface with input name, and returns \
previous interface registered with the same name if replace is False \
else generate a new name for the new interface.
        """

        result = self.get(name, None)

        if name is None:
            name = Component.GENERATE_INTERFACE_NAME(interface, generated=True)

        self[name] = interface

        return result

    def remove_interface(self, name):
        """
        Remove an interface from this component and returns it. \
Raises a NoSuchInterfaceError in case of name does not exist.
        """

        if name not in self:
            raise Component.NoSuchInterfaceError(self, name=name)

        result = self[name]

        del self[name]

        return result

    def start(self):
        """
        Start this component. Do nothing by default.
        """

        pass

    def stop(self):
        """
        Stop this component. Do nothing by default.
        """

        pass

    @staticmethod
    def GENERATE_INTERFACE_NAME(interface, generated=False):
        """
        Generate interface name.
        """

        result = ""

        interface_type = type(interface) if not inspect.isclass(interface) \
            else interface

        result = "{0}.{1}".format(
            getattr(interface_type, '__module__'),
            getattr(interface_type, '__name__'))

        if generated:
            result += "_{0}".format(uuid())

        return result
