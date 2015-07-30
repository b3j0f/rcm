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

"""This module provides classes in charge of proxifying resources around
components.

It becomes easier to separate resources from the mean of providing/consuming
them.

Such operations are granted through the proxy design pattern in order to
separate ``what`` and ``how`` a component is bound/provided with its
environment.

The ``what`` is specified through the Port class. This one uses interfaces in
order to describe bound resources. The ``how`` is ensured with Binding objects
which are used by Port objects.
"""

__all__ = [
    'SetIOCtrl', 'Input', 'Output'
]

from b3j0f.annotation.check import Target, MaxCount
from b3j0f.rcm.ctl.annotation import CtrlAnnotationInterceptor
from b3j0f.rcm.ctl.annotation import (
    CtrlAnnotation, Ctrl2CAnnotation, C2CtrlAnnotation
)
from b3j0f.rcm.io.port import Port
from b3j0f.rcm.io.ctrl import IOController


class Input(CtrlAnnotationInterceptor):
    """InputPort injector which uses a name in order to inject an InputPort
    proxy.
    """

    NAME = 'name'  #: input port name field name

    def __init__(self, name, *args, **kwargs):
        """
        :param str name: port name to retrieve.
        """

        super(Input, self).__init__(*args, **kwargs)

        self.name = name

    def get_target_ctx(self, component, *args, **kwargs):

        port = component.get(self.name)

        target = None if port is None else port._renewproxy

        result = target, port

        return result


class Output(Ctrl2CAnnotation):
    """Output descriptor.
    """

    STATELESS = 'stateless'  #: port stateless mode
    INTERFACES = 'interfaces'  #: port interfaces
    POLICYRULES = 'policyrules'  #: port policyrules

    def __init__(
            self, name=None, stateless=False, interfaces=None,
            policyrules=None,
            *args, **kwargs
    ):
        """
        :param str name: output port name.
        :param bool stateless: stateless if True (False by default).
        :param tuple interfaces: port interfaces.
        :param PolicyRules policyrules: port policyrules.
        """

        super(Output, self).__init__(*args, **kwargs)

        self.name = name
        self.stateless = stateless
        self.interfaces = interfaces
        self.policyrules = policyrules

    def process_result(self, result, component, *args, **kwargs):

        # create a port and bind it to the component
        port = Port(
            resource=result, itfs=self.interfaces,
            policyrules=self.policyrules
        )
        component.set_port(port=port, name=self.name)


@MaxCount()
@Target([Target.ROUTINE, type])
class Async(Ctrl2CAnnotation):
    """Specify asynchronous mode on class methods.
    """

    def __init__(self, name=None, *args, **kwargs):
        """
        :param str name: specific port name.
        """

        super(Async, self).__init__(*args, **kwargs)

        self.name = name

    def process_result(self, result, component, getter, *args, **kwargs):

        getter_name = getter.__name__
        # create a port and bind it to the component
        port = Port.GET_PORTS(component=component, names=self.name)
        apply_policy(port.policyrules)


@Target(type)
class Ports(CtrlAnnotation):
    """Annotation in charge of binding Port in a component Port.
    """

    Port = 'Port'

    #__slots__ = (Port, ) + CtrlAnnotation.__slots__

    def __init__(self, port, *args, **kwargs):
        """
        :param dict port: port to bind to component.
        """

        super(Ports, self).__init__(*args, **kwargs)

        self.port = port

    def apply(self, component, *args, **kwargs):

        # iterate on all self port
        self_port = self.port
        for port_name in self_port:
            port = self_port[port_name]
            # bind it with its name
            component[port_name] = port

    def unapply(self, component, *args, **kwargs):

        # iterate on all self port
        self_port = self.port
        for port_name in self_port:
            # bind it with its name
            del component[port_name]


class SetIOCtrl(C2CtrlAnnotation):
    """Inject Binding controller in component implementation.
    """

    def get_value(self, component, *args, **kargs):

        return IOController.get_ctrl(component)


class Input(CtrlAnnotationInterceptor):
    """Dedicated to inject a port proxy into an implementation.
    """

    def __init__(self, port, *args, **kwargs):
        """
        :param str port: port name from where get a proxy to inject in the
            implementation.
        """

        super(Input, self).__init__(*args, **kwargs)

    def get_target_ctx(self, component, *args, **kwargs):

        return component.set_port, component


class Output(CtrlAnnotationInterceptor):
    """Called when a port is unbound from component.

    Specific parameters are Component.remove_port parameters:

    - name: port name to remove.
    """

    def get_target_ctx(self, component, *args, **kwargs):

        return component.remove_port, component
