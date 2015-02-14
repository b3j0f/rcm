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
from b3j0f.rcm.controller.core import Controller
from b3j0f.rcm.controller.impl import ParameterizedImplAnnotation, Context


class BindingController(Controller):
    """Dedicated to manage component interface bindings.
    """

    __slots__ = Controller.__slots__

    class BindingError(Exception):
        pass

    def bind(self, port_name, binding):
        """
        Bind a binding to a component interface_name.
        """

        check = lambda ann: ann.name == port_name

        for component in self.components:
            # set binding to component
            component[port_name] = binding
            # apply Input annotations
            if isinstance(binding, InputPort):
                Input.apply(component=component, check=check)
            # apply Output annotations
            elif isinstance(binding, OutputPort):
                Output.apply(component=component, check=check)

            else:
                raise BindingController.BindingError()

    def unbind(self, port_name):
        """
        Unbind a binding_name from an port_name.
        """

        check = lambda ann: ann.name == port_name

        for component in self.components:

            Input.unapply(component=component, check=check)

            Output.unapply(component=component, check=check)

            del component[port_name]

    @staticmethod
    def bind_to(component, port_name, binding):

        bc = BindingController.get_controller(component)
        if bc is not None:
            bc.bind(port_name, binding)

    @staticmethod
    def unbind_from(component, port_name):

        bc = BindingController.get_controller(component)
        if bc is not None:
            bc.unbind(port_name)


class Binding(Context):
    """Inject Binding controller in component implementation.
    """
    __slots__ = Context.__slots__

    def __init__(self, name=BindingController.get_name(), *args, **kwargs):

        super(Binding, self).__init__(name=name, *args, **kwargs)


class InputPort(Component):
    """Input port.
    """

    __slots__ = Component.__slots__


class Input(ParameterizedImplAnnotation):
    """Impl In injector which uses a name in order to inject a In Port.
    """

    NAME = 'name'  #: input port name field name

    __slots__ = (NAME, ) + ParameterizedImplAnnotation.__slots__

    def __init__(self, name, *args, **kwargs):

        super(Input, self).__init__(*args, **kwargs)

        self.name = name

    def get_port_name(self, *args, **kwargs):

        return self.name


class OutputPort(Component):
    """Output port.
    """

    __slots__ = Component.__slots__

    def bind(self, component, port_name, *args, **kwargs):

        Output.apply(component=component)

    def unbind(self, component, port_name, *args, **kwargs):

        Output.unapply(component=component)


class Output(ParameterizedImplAnnotation):
    """Impl Out descriptor.
    """

    RESOURCE = '_resource'  #: output port resource field name

    __slots__ = (RESOURCE, ) + ParameterizedImplAnnotation.__slots__

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
