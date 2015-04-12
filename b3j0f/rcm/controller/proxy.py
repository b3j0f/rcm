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

"""This module provides classes in charge of binding/providing Components to
the execution environment.

Such operations are granted through the proxy design pattern in order to
separate ``what`` and ``how`` a component is bound/provided with its
environment.

The ``what`` is specified through the Proxy class. This one uses interfaces in
order to describe a resource is bound/provided. InputProxy and OutputProxy
are respectively used to bound and provided resources.
The ``how`` is ensured by Binding objects which are used by proxy objects.
"""

__all__ = [
    'Proxy', 'Binding',
    'OutputProxy', 'InputProxy',
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

from b3j0f.annotation.check import Target, MaxCount
from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup
from b3j0f.utils.proxy import get_proxy
from b3j0f.rcm.core import Component
from b3j0f.rcm.controller.annotation import (
    CtrlAnnotation, Ctrl2CAnnotation, C2CtrlAnnotation
)
from b3j0f.rcm.controller.impl import ImplController


class Proxy(Component):
    """Base class of InputProxy and OutputProxy.

    Its role is to bind/provide a component with the environment resources in
    easying separation of what and how a resource is bound/provided to/by a
    component.

    A proxy description uses a set of interfaces in order to filter which kind
    of resources can be bound/provided to/by a component.
    Bindings are proxy ports.
    """

    INTERFACES = '_interfaces'  #: interfaces field name
    _LOCK = '_lock'  #: private lock field name

    def __init__(
        self, interfaces=None, *args, **kwargs
    ):
        """
        :param interfaces: proxy interface names/classes.
        :type interfaces: list or str
        """

        super(Proxy, self).__init__(*args, **kwargs)

        self._lock = Lock()
        self.interfaces = interfaces

    @property
    def interfaces(self):
        """Return an array of self interfaces.

        :return: list of proxy interfaces.
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

    def get_resource(self, bindings=None):
        """Get proxy resource related to binding name(s).

        :param bindings: Bound resource (regex) name(s). If None, get default
        resource which is the component model programming language.
        :type bindings: list or str or Binding
        :return: a resource if bindings is None, else a dictionary of
        resources by binding names.
        """

        result = None

        if bindings is None:
            raise NotImplementedError()

        else:  # if specific bindings are requested
            if isinstance(bindings, basestring):
                names = (bindings)
            elif isclass(bindings) and issubclass(bindings, Binding):
                types = (bindings)
            else:  # names and types are initialized with input binding types
                names, types = [], []
                for binding in bindings:
                    # add to names if binding is a str
                    if isinstance(binding, basestring):
                        names.append(binding)
                    # or to types if binding is a subclass of binding
                    elif isclass(binding) and issubclass(binding, Binding):
                        types.append(binding)
                    # else the type does not correspond to expected ones
                    else:
                        raise TypeError(
                            "Wrong value {0}. str/ Binding type expected."
                            .format(binding)
                        )
            # get ports by names and types
            result = self.get_ports(
                names=names, types=types,
                select=lambda n, p: isinstance(p, Binding)
            )

        return result

    def check_resource(self, resource):
        """Check input resource related to self interfaces.
        """

        return isinstance(resource, self.interfaces)

    def check_resource_cls(self, resource_cls):

        result = True

        for interface in self.interfaces:
            result = issubclass(resource_cls, interface)

            if not result:
                break

        return result


class Binding(Component):
    """Specify how a resource is bound/provided to/by a component.
    """

    def __init__(self, proxy, *args, **kwargs):
        """
        :param Proxy proxy: proxy which uses the binding.
        """

        self.proxy = proxy

    def start(self, proxy, resource):
        """Start the binding with input proxy and proxy resource, and return
        the binding resource.

        :param Proxy proxy: resource proxy.
        :param resource: proxy resource.
        :return: proxyfied resource transformed by this binding.
        """

    def stop(self, proxy, resource):
        """Stop the binding execution.
        """

    def get_resource(self, proxy, resource):
        """Get proxy resource.

        :param Proxy proxy: resource proxy.
        :param resource: proxy resource.
        :return: proxyfied resource transformed by this binding.
        """

        raise NotImplementedError()

    @classmethod
    def get_name(cls):
        """Get binding name. Class name in lower case by default.

        :return: class name in lower case by default.
        :rtype: str
        """
        return cls.__name__.lower()


class PromotedProxy(Proxy):
    """A promoted proxy is dedicated to promote other proxies.
    """

    CMP_PORT_SEPARATOR = '/'

    def promote(self, component, promoted=""):
        """Promote this port to input component proxy where names match with
        input promoted.

        :param Component component: component from where find promoted.
        :param promoted: promoted to promote.
        :type promoted: list or str of type [port_name/]sub_port_name
        """

        # ensure promoted is a list of str
        if isinstance(promoted, basestring):
            promoted = [promoted]

        for source in promoted:
            # first, identify component name with proxy
            splitted_source = source.split(Proxy.CMP_PORT_SEPARATOR)
            if len(splitted_source) == 1:
                # by default, search among the impl controller
                component_rc = re_compile(
                    '^{0}'.format(ImplController.ctrl_name())
                )
                port_rc = re_compile(splitted_source[0])
            else:
                component_rc = re_compile(splitted_source[0])
                port_rc = re_compile(splitted_source[1])

            proxy = self._component_cls().get_cls_proxy(
                component=component,
                select=lambda name, component:
                (
                    component_rc.match(name)
                    and self._component_filter(name, component)
                )
            )
            # bind port
            for name in proxy:
                port = proxy[name]
                if port_rc.match(name) and self._port_filter(name, port):
                    self[name] = port

    def _component_cls(self):

        return Component

    def _port_cls(self):

        return Proxy

    def _component_filter(self, name, component):

        return True

    def _port_filter(self, name, port):

        return True


class InputProxy(Proxy):
    """Input port.
    """


class Input(C2CtrlAnnotation):
    """InputProxy injector which uses a name in order to inject a InputProxy.
    """

    NAME = 'name'  #: input port name field name

    __slots__ = (NAME, ) + Ctrl2CAnnotation.__slots__

    def __init__(self, name, *args, **kwargs):

        super(Input, self).__init__(*args, **kwargs)

        self.name = name

    def get_port_name(self, *args, **kwargs):

        return self.name


class ProxyBinding(Component):
    """Proxy binding which describe the mean to promote component content.

    Such port binding has a name and a proxy.
    The proxy is generated thanks to the bound port interfaces and the content
    to promote.
    """

    NAME = 'name'  #: binding name field name
    PROXY = '_proxy'  #: proxy value field name

    def __init__(self, name, *args, **kwargs):

        super(ProxyBinding, self).__init__(*args, **kwargs)

        self.name = name

    def bind(self, component, port_name, *args, **kwargs):

        if isinstance(component, OutputProxy):

            self.update_proxy()

    def update_proxy(self, component, interfaces, name):
        """Renew a proxy.
        """

        self._lock.acquire()

        impl = ImplController.get_impl(component)

        if impl is not None:
            self._proxy = get_proxy(impl, interfaces)

        self._lock.release()

    def del_proxy(self):
        """Delete self proxy.
        """
        pass

    def unbind(self, component, port_name, *args, **kwargs):

        if isinstance(component, OutputProxy):

            self.del_proxy()


class OutputProxy(Proxy):
    """Output port which provides component content thanks to port bindings.

    Those bindings are bound to the output port such as any component.
    """

    ASYNC = 'async'  #: asynchronous mode attribute name
    INPUTS = 'inputs'  #: inputs attribute name

    def __init__(self, async=False, stateless=False, *args, **kwargs):

        super(OutputProxy, self).__init__(*args, **kwargs)

        self.async = async
        self.stateless = stateless

    def bind(self, component, port_name, *args, **kwargs):

        Output.apply(component=component)

    def unbind(self, component, port_name, *args, **kwargs):

        Output.unapply(component=component)


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
class Proxies(CtrlAnnotation):
    """Annotation in charge of binding proxy in a component proxy.
    """

    PROXY = 'proxy'

    __slots__ = (PROXY, ) + CtrlAnnotation.__slots__

    def __init__(self, proxy, *args, **kwargs):
        """
        :param proxy: proxy to bind to component.
        :type proxy: dict
        """
        super(Proxies, self).__init__(*args, **kwargs)

        self.proxy = proxy

    def apply(self, component, *args, **kwargs):

        # iterate on all self proxy
        self_proxy = self.proxy
        for port_name in self_proxy:
            port = self_proxy[port_name]
            # bind it with its name
            component[port_name] = port

    def unapply(self, component, *args, **kwargs):

        # iterate on all self proxy
        self_proxy = self.proxy
        for port_name in self_proxy:
            # bind it with its name
            del component[port_name]
