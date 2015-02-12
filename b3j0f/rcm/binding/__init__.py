# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2015 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

__all__ = ['Interface', 'Binding']

from b3j0f.rcm.core import Component


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
