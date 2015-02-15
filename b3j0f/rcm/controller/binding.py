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

from abc import ABCMeta

from inspect import getmembers, isroutine, isclass

from functools import wraps

try:
    from threading import Lock
except ImportError:
    from dummy_threading import Lock

from b3j0f.utils.version import basestring, PY2
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


class Port(Component):
    """Base class for InputPort and OutputPort.

    Its role is to bind the component with the environment resources.

    It uses interfaces in order to describe what is promoted.
    """

    INTERFACES = '_interfaces'  #: interfaces field name
    _LOCK = '_lock'  #: private lock field name

    __slots__ = (INTERFACES, _LOCK) + Component.__slots__

    def __init__(self, interfaces=None, *args, **kwargs):

        super(Port, self).__init__(*args, **kwargs)

        self._lock = Lock()
        self.interfaces = interfaces

    @property
    def interfaces(self):

        return self._interfaces

    @interfaces.setter
    def interfaces(self, value):

        self._lock.acquire()
        self._interfaces = value
        self._lock.release()


class InputPort(Port):
    """Input port.
    """

    __slots__ = Port.__slots__


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


class PortBinding(Component):
    """Port binding which describe the mean to promote component content.

    Such port binding has a name and a proxy.
    The proxy is generated thanks to the bound port interfaces and the content
    to promote.
    """

    NAME = 'name'  #: binding name field name
    PROXY = '_proxy'  #: proxy value field name

    __slots__ = (NAME, PROXY) + Component.__slots__

    def __init__(self, name, *args, **kwargs):

        super(PortBinding, self).__init__(*args, **kwargs)

        self.name = name

    def bind(self, component, port_name, *args, **kwargs):

        if isinstance(component, OutputPort):

            self.update_proxy()

    def update_proxy(self, interfaces, name):
        """Renew a proxy.
        """

        self._lock.acquire()

        # if one interface is a class, generate a class proxy,
        # otherwise generate a function wrapper
        content = {}
        isClass = False
        for interface in interfaces:
            if isclass(interface):
                isClass = True
                for name, member in getmembers(
                    interface, lambda m: isroutine(m)
                ):
                    content[name] = member
            elif isroutine(interface):
                interface_name = interface.__name__
                content[interface_name] = interface

        if isClass:
            self._proxy = _ContentProxy(bases=interface)
        else:
            self._proxy = _ContentProxyMeta.get_proxy(interfaces)

        self._lock.release()

    def del_proxy(self):
        """Delete self proxy.
        """
        pass

    def unbind(self, component, port_name, *args, **kwargs):

        if isinstance(component, OutputPort):

            self.del_proxy()


class OutputPort(Port):
    """Output port which provides component content thanks to port bindings.

    Those bindings are bound to the output port such as any component.
    """

    __slots__ = Component.__slots__

    def bind(self, component, port_name, *args, **kwargs):

        Output.apply(component=component)

    def unbind(self, component, port_name, *args, **kwargs):

        Output.unapply(component=component)


class _ContentProxyMeta(ABCMeta):
    """Meta class for port binding proxies.
    """

    def __call__(cls, bases, instance, *args, **kwargs):
        """A proxy may be called with base types and a reference to an
        instance.

        :param cls: cls to instantiate.
        :param bases: base types to enrich in the result cls.
        """

        result = super(OutputPort.ProxyMeta, cls).__call__(*args, **kwargs)
        # ensure bases are a set of types
        if issubclass(bases, type):
            bases = [bases]
        # enrich cls with base types
        for base in bases:
            # register base in cls
            cls.register(base)
            # enrich methods/functions
            for name, member in getmembers(
                base, lambda member: isroutine(member)
            ):
                if not hasattr(cls, name):
                    proxy = OutputPort.ProxyMeta.get_proxy(member)
                    if proxy is not None:
                        setattr(cls, name, proxy)

        return result

    @staticmethod
    def get_proxy(target, instance=None, name=None):

        @wraps(target, {}, {})
        def result(*args, **kwargs):
            if instance is None:
                result = target(*args, **kwargs)
            else:
                result = getattr(instance, name)(*args, **kwargs)

            return result

        return result

if PY2:
    class _ContentProxy(object):
        """Output proxy class.
        """

        __metaclass__ = _ContentProxyMeta

else:
    class _ContentProxy(object, metaclass=_ContentProxyMeta):
        """Output proxy class."""


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
