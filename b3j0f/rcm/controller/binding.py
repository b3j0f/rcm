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

from b3j0f.rcm.binding.core import Interface
from b3j0f.rcm.controller.core import Controller
from b3j0f.annotation import Annotation


class BindingController(Controller):
    """
    Dedicated to manage component interface bindings.
    """

    NAME = '/binding-controller'

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


class Reference(Annotation):
    """
    Decorator dedicated to set a reference into business code.
    """

    def __init__(self, name=None, interface=None):

        self._super(Reference).__init__()
        self.name = name
        self.interface = interface


class Service(Annotation):
    """
    Decorator dedicated to provides a function such as a Service.
    """

    def __init__(self, name=None, interface=None, *bindings):

        self._super(Service).__init__()
        self.name = name
        self.interface = interface
        self.bindings = bindings
