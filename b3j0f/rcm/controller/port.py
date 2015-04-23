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
    'Port', 'Binding',
    'OutputPort', 'InputPort',
    'Input', 'Output',
    'Proxies',
    'Async'
]

try:
    from threading import Lock
except ImportError:
    from dummy_threading import Lock

from re import compile as re_compile

from inspect import isclass

from collections import Iterable

from b3j0f.annotation.check import Target, MaxCount
from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup
from b3j0f.utils.Port import get_proxy
from b3j0f.rcm.core import Component
from b3j0f.rcm.controller.annotation import (
    CtrlAnnotation, Ctrl2CAnnotation, C2CtrlAnnotation
)
from b3j0f.rcm.controller.impl import ImplController


class Port(Component):
    """Component port which permits to proxify component resources and to
    separate the mean to consume/provide resources from resources.

    A Port uses:

    - a set of interfaces in order to filter which kind
        of resources can be bound/provided to/by a component.
    - a resource to proxify.
    - a proxy.
    - a set of bindings which are the mean to proxify a resource.
    - target ports which use self such as a resource.

    While interfaces and proxy are internal to the port, resource and bindings
    are bound to the port because they are seen such as port functional
    properties.
    """

    INTERFACES = '_interfaces'  #: interfaces field name
    PROXY = '_proxy'  #: proxy field name
    RESOURCE = 'resource'  #: resource port name
    TARGETS = '_targets'  #: targets field name
    _LOCK = '_lock'  #: private lock field name

    def __init__(
        self,
        interfaces=None, resource=None, bindings=None,
        targets=None,
        *args, **kwargs
    ):
        """
        :param interfaces: Port interface names/classes.
        :type interfaces: list or str
        :param resource: resource to proxify.
        :param bindings: binding(s) to use.
        :type bindings: list or Binding
        :param targets: ports which use self such as a resource.
        :type targets: list or Port
        """

        super(Port, self).__init__(*args, **kwargs)

        # set protected attributes
        self._lock = Lock()
        self._proxy = None
        self._targets = set()
        if isinstance(targets, Port):
            self._targets.add(targets)
        elif isinstance(targets, Iterable):
            self._targets |= targets
        # set public attributes
        self.interfaces = interfaces
        self.bindings = bindings
        self.resource = resource

    @property
    def interfaces(self):
        """Return an array of self interfaces.

        :return: list of Port interfaces.
        :rtype: list
        """

        return list(self._interfaces)

    @interfaces.setter
    def interfaces(self, value):
        """Update interfaces with a list of interface names/types.

        :param value: new interfaces to use.
        :type value: list or str or type
        """

        self._lock.acquire()

        # ensure interfaces are a set of types
        if value is None:  # none value is a set with object
            value = set([object])
        elif isinstance(value, basestring):
            value = set([lookup(value)])
        elif isclass(value):
            value = set([value])
        # convert all str to tuple of types
        self._interfaces = (
            v if isclass(v) else lookup(v) for v in value
        )

        self._lock.release()

    @property
    def proxy(self):
        """Get proxy.

        :return: proxy.
        """
        return self._proxy

    @property
    def resource(self):
        """Get resource.

        :return: self resource.
        """

        result = self[Port.RESOURCE]

        return result

    @resource.setter
    def resource(self, resource):
        """Change of resource in checking if input resource is consistent with
        self requirements.

        :param resource: new resource to use.
        :return: old resource if exist or None if input resource is
            inconsistent.
        """

        result = self.resource

        if self.check_source(resource):
            # set resource
            self[Port.RESOURCE] = resource
            # set proxy
            self._proxy = self._get_proxy(resource=resource)
            # propagate the new proxy on target ports
            for target in self._targets:
                target.resource = self
        else:  # if resource is inconsistent, nonify result.
            result = None

        return result

    def _get_proxy(self, resource):
        """Get resource proxy. Called internally by self resource setter
        property.

        :param resource: resource to proxify.
        """

        # if resource is a proxy port
        if isinstance(resource, Port):
            toproxify = resource.proxy
        else:
            toproxify = resource

        # generate the right Port toproxify
        result = get_proxy(elt=toproxify, bases=self.interfaces)

        return result

    def check_source(self, resource):
        """Check input resource related to self interfaces.
        """

        result = False

        _source = self._get_source(resource)
        # check than _source inherits from all interfaces
        for interface in self.interfaces:
            result = isinstance(_source, interface)
            if not result:
                break

        return result

    def _on_bind(self, component, name, *args, **kwargs):

        # if component is a Port, name is resource and component is not self
        if (
            isinstance(component, Port)
            and name == Port.RESOURCE
            and component is not self
        ):
            # add component to targets
            self._targets.add(component)

    def _on_unbind(self, component, name, *args, **kwargs):

        # if component is a Port, name is resource
        if isinstance(component, Port) and name == Port.RESOURCE:
            # remove component from targets
            self._targets.remove(component)


class InputPort(Port):
    """Port dedicated to consume resources.
    """
    pass


class OutputPort(Port):
    """Port dedicated to provide resources.
    """
    pass


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
    """Impl Out descriptor.
    """

    ASYNC = 'async'  #: asynchronous mode
    STATELESS = 'stateless'  #: stateless mode
    RESOURCE = '_resource'  #: output port resource field name

    __slots__ = (RESOURCE, ) + Ctrl2CAnnotation.__slots__

    def __init__(self, async, stateless, resource, *args, **kwargs):

        self.resource = resource
        self.async = async
        self.stateless = stateless

    @property
    def resource(self):

        return self._resource

    @resource.setter
    def resource(self, value):

        if isinstance(value, basestring):
            value = lookup(value)

        self._resource = value


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
