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
    'BindingController', 'SetPortCtrl',
    'InputPort', 'OutputPort', 'Input', 'Output'
]

from collections import Iterable

from b3j0f.annotation.check import Target, MaxCount
from b3j0f.utils.version import basestring
from b3j0f.rcm.core import Component
from b3j0f.rcm.controller.core import Controller
from b3j0f.rcm.binding.core import Port
from b3j0f.rcm.controller.annotation import (
    CtrlAnnotation, Ctrl2CAnnotation, C2CtrlAnnotation
)
from b3j0f.rcm.controller.impl import ImplController
from b3j0f.rcm.controller.name import NameController


class BindingController(Controller):
    """In charge of easiing port promoting/wiring.
    """

    class BindingError(Exception):
        pass

    def get_sub_ports(
        self, components=None,
        portnames=None, porttypes=None, portcond=None
    ):
        """Get all component ports of sub components of self components.

        :param components: component(s) or component name(s) from where search
            ports. If None, search among all self components.
        :type components: str, Component or Iterable
        :param portnames: port name(s) to find.
        :type portnames: str or Iterable
        :param porttypes: port types to find.
        :type porttypes: type or Iterable
        :param portcond: search function which takes in parameters a component,
            a port name and a port.
        :return: set of ports by name by component.
        :rtype: dict
        """

        # initialize result with an empty dictionary
        result = {}

        self_components = self.components
        # if components is None, use self components
        if components is None:
            _components = self_components
        else:
            _components = []
            # ensure components is a list
            if isinstance(components, basestring, Component):
                components = [components]
            # parse content of components
            if isinstance(components, Iterable):
                for component in components:
                    # ensure component is in self components
                    if isinstance(component, Component):
                        if component in self_components:
                            _components.append(component)
                    # if component is a name, get related components
                    elif isinstance(component, basestring):
                        for self_component in self.components:
                            name_component = NameController.get_name(
                                self_component
                            )
                            if name_component == component:
                                _components.append(self_component)
            else:
                raise TypeError(
                    "Wrong type of components {0}.".format(components)
                )
        # search for inner ports
        for component in _components:
            for portname in component:
                subcomponent = component[portname]
                ports = subcomponent.get_ports(
                    names=portnames, types=porttypes,
                    select=lambda name, port: portcond(component, name, port)
                )
                # if ports have been founded
                if ports:
                    # add them to the result
                    if component not in result:
                        result[component] = {}
                    result[component][subcomponent] = ports

        return result

    def wire(self, components=None, inputports=None, outputports=None):
        """Wire input and ouptut ports among them.

        Input and output ports are bound to components in the same component.

        :param inputports: input port name. If None, apply method on all
            input ports.
        :type inputports: str, InputPort or Iterable
        :param outputports: output port name. If None, apply method on all
            output ports.
        :type outputports: str, OutputPort or Iterable
        :param components: component(s) or component name(s) from where search
            ports. If None, search among all self components.
        :type components: str, Component or Iterable
        """

        cinputports = self.get_sub_ports(
            components=components, portnames=inputport, porttypes=InputPort
        )
        coutputports = self.get_sub_ports(
            components=components, portnames=outputport, porttypes=OutputPort
        )
        # bind all input ports to all output ports
        for component in cinputports:
            if component in coutputports:
                sinputports = cinputports[component]
                soutputports = coutputports[component]
                for subcomponent in sinputports:
                    inputports = sinputports[subcomponent]
                    for name in inputports:
                        inputport = inputports[name]
                        for subcomponent in soutputports:
                            outputports = soutputports[subcomponent]
                            for name in outputports:
                                outputport = outputports[name]
                                try:
                                    inputport.resource = outputport
                                except Port.ResourceError:
                                    pass

    def promote(self, sources=None, targets=None, components=None):
        """Promote source ports to target ports.

        :param sources: source ports to promote to target ports.
        :type sources: Port or str or Iterable
        :param targets: target ports to be promoted by source ports.
        :type targets: Port or str or Iterable
        :param components: components from where find targets and sources.
        :type components: str or Component or Iterable
        """

        pass

    def unpromote(self, components=None, sources=None, targets=None):
        """Unpromote target from source ports.
        """

        pass

    @staticmethod
    def WIRE(components=None, inputports=None, outputports=None):

        BindingController._PROCESSS(
            _components=components, _method='wire',
            inputports=inputports, outputports=outputports
        )

    @staticmethod
    def UNWIRE(components=None, inputports=None, outputports=None):

        BindingController._PROCESSS(
            _components=components, _method='unwire',
            inputports=inputports, outputports=outputports
        )

    @staticmethod
    def PROMOTE(components=None, sources=None, targets=None):

        BindingController._PROCESSS(
            _components=components, _method='promote',
            sources=sources, targets=targets
        )

    @staticmethod
    def UNPROMOTE(components=None, sources=None, targets=None):

        BindingController._PROCESSS(
            _components=components, _method='unpromote',
            sources=sources, targets=targets
        )


class InputPort(Port):
    """Port dedicated to consume resources.
    """

    pass


class OutputPort(Port):
    """Port dedicated to provide resources.
    """

    pass


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

    __slots__ = (Port, ) + CtrlAnnotation.__slots__

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


class SetPortCtrl(C2CtrlAnnotation):
    """Inject Binding controller in component implementation.
    """

    def get_value(self, component, *args, **kargs):

        return BindingController.get_controller(component)


class PromotedPort(Port):
    """A promoted Port is dedicated to promote other proxies.
    """

    CMP_PORT_SEPARATOR = '/'

    def promote(self, component, promoted=""):
        """Promote this port to input component Port where names match with
        input promoted.

        :param Component component: component from where find promoted.
        :param promoted: promoted to promote.
        :type promoted: list or str of type [port_name/]sub_port_name
        """

        # ensure promoted is a list of str
        if isinstance(promoted, basestring):
            promoted = [promoted]

        for resource in promoted:
            # first, identify component name with Port
            splitted_source = resource.split(PromotedPort.CMP_PORT_SEPARATOR)
            if len(splitted_source) == 1:
                # by default, search among the impl controller
                component_rc = re_compile(
                    '^{0}'.format(ImplController.ctrl_name())
                )
                port_rc = re_compile(splitted_source[0])
            else:
                component_rc = re_compile(splitted_source[0])
                port_rc = re_compile(splitted_source[1])

            Port = self._component_cls().get_cls_Port(
                component=component,
                select=lambda name, component:
                (
                    component_rc.match(name)
                    and self._component_filter(name, component)
                )
            )
            # bind port
            for name in Port:
                port = Port[name]
                if port_rc.match(name) and self._port_filter(name, port):
                    self[name] = port

    def _component_cls(self):

        return Component

    def _port_cls(self):

        return Port

    def _component_filter(self, name, component):

        return True

    def _port_filter(self, name, port):

        return True
