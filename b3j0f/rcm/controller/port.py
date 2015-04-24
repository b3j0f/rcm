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
    'Port',
    'OutputPort', 'InputPort',
    'Input', 'Output',
    'Async'
]

try:
    from threading import Lock
except ImportError:
    from dummy_threading import Lock

from inspect import isclass

from collections import Iterable

from b3j0f.annotation.check import Target, MaxCount
from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup
from b3j0f.utils.proxy import get_proxy
from b3j0f.rcm.core import Component
from b3j0f.rcm.controller.annotation import (
    CtrlAnnotation, Ctrl2CAnnotation, C2CtrlAnnotation
)


class Port(Component):
    """Component port which permits to proxify component resources and to
    separate the mean to consume/provide resources from resources.

    A Port uses:

    - a set of interfaces in order to filter which kind
        of resources can be bound/provided to/by a component.
    - a resource to proxify.
    - a proxy.
    - a set of bindings which are the mean to proxify a resource.

    While interfaces and proxy are internal to the port, resource and bindings
    are bound to the port because they are seen such as port functional
    properties.
    """

    class ResourceError(Exception):
        """Raised if new port resource is inconsistent with port requirements.
        """
        pass

    INTERFACES = '_interfaces'  #: interfaces field name
    PROXY = '_proxy'  #: proxy field name
    RESOURCE = 'resource'  #: resource port name
    _LOCK = '_lock'  #: private lock field name

    def __init__(
        self,
        interfaces=None, resource=None, bindings=None,
        *args, **kwargs
    ):
        """
        :param interfaces: Port interface names/classes.
        :type interfaces: list or str
        :param resource: resource to proxify.
        :param bindings: binding(s) to use.
        :type bindings: list or Binding
        """

        super(Port, self).__init__(*args, **kwargs)

        # set protected attributes
        self._lock = Lock()
        self._proxy = None
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
            value = set([value])
        elif isclass(value):
            value = set([value])
        elif isinstance(value, Iterable):
            value = set(value)
        else:
            self._lock.release()
            raise TypeError(
                "Wrong value ({0}) type {0}".format(value, type(value))
            )

        interfaces = [None] * len(value)

        # convert all str to related class
        for index, v in enumerate(value):
            if isinstance(v, basestring):
                try:
                    v = lookup(v)
                except ImportError:
                    self._lock.release()
                    raise
            if not isclass(v):
                self._lock.release()
                raise TypeError(
                    "Wrong value ({0}) type {0}.".format(v, type(v))
                )
            interfaces[index] = v

        # convert interfaces to a tuple
        self._interfaces = tuple(interfaces)

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
        """

        if self.check_resource(resource):
            # set resource
            self[Port.RESOURCE] = resource
            # set proxy
            self._proxy = self._get_proxy(resource=resource)
            # propagate the new proxy on target ports
            for component in self._bound_on:
                if isinstance(component, Port):
                    component.resource = self
        else:
            raise Port.ResourceError(
                "Resource {0} not checked by {1}.".format(resource, self)
            )

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

    def check_resource(self, resource):
        """Check input resource related to self interfaces.

        :param resource: resource to check.
        """

        result = False

        _source = resource._proxy if isinstance(resource, Port) else resource
        # check than _source inherits from all interfaces
        for interface in self.interfaces:
            result = isinstance(_source, interface)
            if not result:
                break

        return result

    def get_proxy(self, binding=None):
        """Get resource proxy relate to input binding. If binding is None, get
        default proxy.

        :param Binding binding:
        """

        if binding is None:
            result = self._proxy

        else:
            result = self.bindings[binding].get_proxy()

        return result


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
