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
from b3j0f.rcm.ctrl.annotation import (
    CtrlAnnotation, Ctrl2CAnnotation, C2CtrlAnnotation
)
from b3j0f.rcm.io.ctrl import IOController


class Input(C2CtrlAnnotation):
    """InputPort injector which uses a name in order to inject a InputPort.
    """

    NAME = 'name'  #: input port name field name

    __slots__ = (NAME, ) + Ctrl2CAnnotation.__slots__

    def __init__(self, name, *args, **kwargs):

        super(Input, self).__init__(*args, **kwargs)

        self.name = name

    def get_port_name(self, *args, **kwargs):

        return self.name


class Output(Ctrl2CAnnotation):
    """Output descriptor.
    """

    ASYNC = 'async'  #: asynchronous mode
    STATELESS = 'stateless'  #: stateless mode
    INTERFACES = 'interfaces'  #: interfaces

    __slots__ = (INTERFACES, ASYNC, STATELESS, ) + Ctrl2CAnnotation.__slots__

    def __init__(
        self, async=None, stateless=None, interfaces=None, *args, **kwargs
    ):

        self.async = async
        self.stateless = stateless
        self.interfaces = interfaces


@MaxCount()
@Target([Target.ROUTINE, type])
class Async(CtrlAnnotation):
    """Specify asynchronous mode on class methods.
    """


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

        return IOController.get_controller(component)
