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
    'Binding'
]

from b3j0f.utils.proxy import get_proxy
from b3j0f.rcm.core import Component
from b3j0f.rcm.controller.core import Controller
from b3j0f.rcm.controller.impl import Context, ImplController, Port
from b3j0f.rcm.controller.proxy import InputProxy, OutputProxy, Proxy


class BindingController(Controller):
    """Manage component interface bindings between proxies of ports.
    """

    __slots__ = Controller.__slots__

    class BindingError(Exception):
        pass

    def bind(self, inputproxy, outputproxy):
        """
        Bind an input to an output.

        :param InputProxy inputproxy:
        :param OutputProxy outputproxy:
        """

        inputproxy.bind(outputproxy)

    def promote(self, component, port_name, proxy):
        """Promote input proxy to input component port name.

        :param Component component: component from where bind a new proxy.
        :param str port_name: port name to bind to input proxy.
        :param Proxy proxy: proxy to bind to port name.
        """

        # check if old port exists
        old_port = component.get(port_name, None)
        if old_port is not None:
            if isinstance(old_port, Proxy):
                old_port[port_name] = proxy
        else:
            if isinstance(proxy, InputProxy):
                port = PromotedInputProxy()
            elif isinstance(proxy, OutputProxy):
                port = PromotedOutputProxy()
            else:
                raise TypeError(
                    "Input proxy may be an InputPort or OutputPort"
                )
            port[port_name] = proxy
            component[port_name] = port

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


class Binding(Context):
    """Inject Binding controller in component implementation.
    """

    __slots__ = Context.__slots__

    def __init__(self, name=BindingController.ctrl_name(), *args, **kwargs):

        super(Binding, self).__init__(name=name, *args, **kwargs)


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


class PromotedProxy(object):
    """Promoted Proxy.
    """

    def get_proxy(self):
        """Get proxy related to self ports of proxy.
        """

        result = []

        for source in Proxy.get_cls_ports(self):
            source_proxy = source.get_proxy()
            result.append(source_proxy)

        return result


class PromotedOutputProxy(OutputProxy, PromotedProxy):
    """Output port which provides component content thanks to port bindings.

    Those bindings are bound to the output port such as any component.
    """

    __slots__ = OutputProxy.__slots__


class PromotedInputProxy(InputProxy, PromotedProxy):
    """Output port which provides component content thanks to port bindings.

    Those bindings are bound to the output port such as any component.
    """

    __slots__ = InputProxy.__slots__
