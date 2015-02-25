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

try:
    from threading import Lock
except ImportError:
    from dummy_threading import Lock

from re import compile as re_compile

from b3j0f.annotation.check import Target
from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup
from b3j0f.utils.proxy import get_proxy
from b3j0f.rcm.core import Component
from b3j0f.rcm.controller.core import Controller
from b3j0f.rcm.controller.impl import (
    ParameterizedImplAnnotation, Context, ImplController, ImplAnnotation
)


class BindingController(Controller):
    """Dedicated to manage component interface bindings between proxies of
    ports.
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
            if isinstance(binding, InputProxy):
                Input.apply(component=component, check=check)
            # apply Output annotations
            elif isinstance(binding, OutputProxy):
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

    def __init__(self, name=BindingController.ctrl_name(), *args, **kwargs):

        super(Binding, self).__init__(name=name, *args, **kwargs)


class Proxy(Component):
    """Base class for InputProxy and OutputProxy.

    Its role is to bind the component with the environment resources.

    It uses interfaces in order to describe what is promoted.
    """

    CMP_PORT_SEPARATOR = ':'  #: char separator between a component and port

    INTERFACES = '_interfaces'  #: interfaces field name
    _SOURCES = '_sources'  #: source proxy
    _LOCK = '_lock'  #: private lock field name

    __slots__ = (
        INTERFACES,  # public attributes
        _LOCK, _SOURCES  # private attributes
    ) + Component.__slots__

    def __init__(
        self, interfaces=None, sources=None, *args, **kwargs
    ):

        super(Proxy, self).__init__(*args, **kwargs)

        self._lock = Lock()
        self.interfaces = interfaces
        self._sources = []
        self.sources = sources

    @property
    def interfaces(self):
        """Return an array of self interfaces
        """

        return [self._interfaces]

    @interfaces.setter
    def interfaces(self, value):
        """Update interfaces with a list of interface names/types.

        :param value:
        :type value: list or str
        """

        self._lock.acquire()

        # ensure interfaces are a set of types
        if isinstance(value, basestring):
            value = set([lookup(value)])
        elif isinstance(value, type):
            value = set([value])
        # convert all str to tuple of types
        self._interfaces = (
            v if isinstance(v, type) else lookup(v) for v in value
        )

        self._lock.release()

    def promote(self, component, sources):
        """Promote this port to input component proxy where names match with
        input sources.

        :param Component component: component from where find sources.
        :param sources: sources to promote.
        :type sources: list or str of type [port_name/]sub_port_name
        """

        #ensure sources are a list of str
        if isinstance(sources, basestring):
            sources = [sources]

        for source in sources:
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
                    component_rc.match(name)
                    and self._component_filter(name, component)
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

    __slots__ = Proxy.__slots__


class Input(ParameterizedImplAnnotation):
    """InputProxy injector which uses a name in order to inject a InputProxy.
    """

    NAME = 'name'  #: input port name field name

    __slots__ = (NAME, ) + ParameterizedImplAnnotation.__slots__

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

    __slots__ = (NAME, PROXY) + Component.__slots__

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


@Target(type)
class Proxys(ImplAnnotation):
    """Annotation in charge of binding proxy in a component proxy.
    """

    PROXY = 'proxy'

    __slots__ = (PROXY, ) + ImplAnnotation.__slots__

    def __init__(self, proxy, *args, **kwargs):
        """
        :param proxy: proxy to bind to component.
        :type proxy: dict
        """
        super(Proxys, self).__init__(*args, **kwargs)

        self.proxy = proxy

    def apply_on(self, component, *args, **kwargs):

        # iterate on all self proxy
        self_proxy = self.proxy
        for port_name in self_proxy:
            port = self_proxy[port_name]
            # bind it with its name
            component[port_name] = port

    def unapply_on(self, component, *args, **kwargs):

        # iterate on all self proxy
        self_proxy = self.proxy
        for port_name in self_proxy:
            # bind it with its name
            del component[port_name]
