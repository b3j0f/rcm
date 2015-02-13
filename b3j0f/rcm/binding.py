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

from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup
from b3j0f.rcm.core import Component
from b3j0f.rcm.controller.impl import ImplAnnotation
from b3j0f.rcm.controller.core import Controller


class BindingController(Controller):
    """Dedicated to manage component interface bindings.
    """

    def bind(self, interface_name, binding):
        """
        Bind a binding to a component interface_name.
        """

        interface = self.get_component().get(interface_name, None)

        if isinstance(interface, Interface):
            binding = binding(interface)

    def unbind(self, interface_name, binding_name):
        """
        Unbind a binding_name from an interface_name.
        """

        interface = self.get_component().get(interface_name, None)

        if isinstance(interface, Interface):
            del interface[binding_name]

    @staticmethod
    def BIND(component, interface_name, binding):

        binding_controller = BindingController.GET_CONTROLLER(component)
        binding_controller.bind(interface_name, binding)

    @staticmethod
    def UNBIND(component, interface_name, binding):

        binding_controller = BindingController.GET_CONTROLLER(component)
        return binding_controller.unbind(interface_name, binding)


class InputPort(Component):
    """Input port.
    """

    __slots__ = Component.__slots__


class Input(ImplAnnotation):
    """Impl In injector which uses a name in order to inject a In Port.
    """

    NAME = 'name'  #: input port name field name

    __slots__ = (NAME, ) + ImplAnnotation.__slots__

    def __init__(self, name, *args, **kwargs):

        super(Input, self).__init__(*args, **kwargs)

        self.name = name

    def get_port_name(self, *args, **kwargs):

        return self.name


class OutputPort(Component):
    """Output port.
    """

    __slots__ = Component.__slots__


class Output(ImplAnnotation):
    """Impl Out descriptor.
    """

    RESOURCE = '_resource'  #: output port resource field name

    __slots__ = (RESOURCE, ) + ImplAnnotation.__slots__

    def __init__(self, resource, *args, **kwargs):

        self.resource = resource

    @property
    def resource(self):
        return self._resource

    @resource.setter
    def resource(self, value):

        if isinstance(value, basestring):
            value = lookup(value)

        self._resource = value
