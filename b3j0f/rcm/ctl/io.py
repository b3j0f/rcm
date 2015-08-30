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

__all__ = ['IOController']

from collections import Iterable

from b3j0f.utils.version import basestring
from b3j0f.rcm.core import Component
from b3j0f.rcm.io.port import Port
from b3j0f.rcm.ctl.core import Controller
from b3j0f.rcm.ctl.name import NameController


class IOController(Controller):
    """In charge of easying component input/output (re-)configuration.
    """

    class Error(Exception):
        """Handle IOController exceptions.
        """

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

        self_components = self._rports.keys()
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
                        for self_component in self_components:
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

        :param inputports: input port name(s). If None, apply method on all
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
            components=components, portnames=inputports, porttypes=Port
        )
        cinputports = [port for port in cinputports if port.isinput]
        coutputports = self.get_sub_ports(
            components=components, portnames=outputports, porttypes=Port
        )
        coutputports = [port for port in coutputports if port.isoutput]
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

    @staticmethod
    def WIRE(components=None, inputports=None, outputports=None):

        IOController._PROCESSS(
            _components=components, _method='wire',
            inputports=inputports, outputports=outputports
        )

    @staticmethod
    def UNWIRE(components=None, inputports=None, outputports=None):

        IOController._PROCESSS(
            _components=components, _method='unwire',
            inputports=inputports, outputports=outputports
        )
