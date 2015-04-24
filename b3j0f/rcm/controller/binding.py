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

__all__ = [
    'BindingController', 'PromotedInputProxy', 'PromotedOutputProxy',
    'Binding', 'SetBindingCtrl'
]

from collections import Iterable

from b3j0f.utils.version import basestring
from b3j0f.rcm.core import Component
from b3j0f.rcm.controller.core import Controller
from b3j0f.rcm.controller.annotation import C2CtrlAnnotation
from b3j0f.rcm.controller.impl import ImplController
from b3j0f.rcm.controller.port import Port, InputPort, OutputPort
from b3j0f.rcm.controller.name import NameController


class BindingController(Controller):
    """Manage component interface bindings between component ports.
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
                        if component in sel_components:
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

    def bind(self, inputport, outputport, components=None):
        """Bind an input port to an output port.

        Input and output ports are bound to components in the same component.

        :param str inputport: input port name.
        :param str outputport: output port name.
        :param components: component(s) or component name(s) from where search
            ports. If None, search among all self components.
        :type components: str, Component or Iterable
        :return: components where binding
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

    def promote(self, sources, targets, port_name, proxy, components=None):
        """Promote input proxy to input component port name.

        :param Component component: component from where bind a new proxy.
        :param str port_name: port name to bind to input proxy.
        :param Proxy proxy: proxy to bind to port name.
        """

        sourceports = self.get_sub_ports(
            components=components, ports=sources
        )

    def unpromote(self, component, port_name):
        """Unpromote port_name.
        """

        del component[port_name]

    @staticmethod
    def promote_to(component, port_name, binding):

        bc = BindingController.get_controller(component)
        if bc is not None:
            bc.promote(port_name, binding)

    @staticmethod
    def unpromote_from(component, port_name):

        bc = BindingController.get_controller(component)
        if bc is not None:
            bc.unpromote(port_name)


class SetBindingCtrl(C2CtrlAnnotation):
    """Inject Binding controller in component implementation.
    """

    def get_value(self, component, *args, **kargs):

        return BindingController.get_controller(component)


class Binding(Component):
    """Specify how a resource is bound/provided to/by a component.

    In order to be processed, a binding is bound to port(s).
    Related ports are choosen at runtime thanks to start/stop methods.

    Therefore, one binding can be used by several ports.
    """

    def __init__(self, parameters=None, *args, **kwargs):
        """
        :param dict parameters: binding parameters.
        """

        super(Binding, self).__init__(*args, **kwargs)

        self.parameters = parameters

    def start(self, port):
        """Start the binding with input port and return the binding resource.

        :param Port port: port using this binding.
        :return: Portfied resource transformed by this binding.
        """

    def stop(self, port):
        """Stop the binding execution.
        """

    def resource(self, port):
        """Get port resource.

        :param Port port: binding resource port.
        :return: port binding resource.
        """

        raise NotImplementedError()


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
