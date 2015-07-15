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

__all__ = ['Port']

from sys import maxsize as maxint

from b3j0f.rcm.io.proxy import getportproxy
from b3j0f.rcm.ctrl.core import Controller


class Port(Controller):
    """Controller which implements the proxy design pattern in order
    to separate component business realization from its consumption/providing.

    A Port uses:

    - interfaces such as port provided/consumed description.
    - input/output port kind(s).
    - a resource to proxify which can come from outside the component model.
    - bound port(s) to proxify such as component model resources.
    - a multiple boolean flag which specifies port proxifier cardinality. If
        True, get_proxy returns one proxy, otherwise a tuple of proxies. False
        by default.
    - an inferior/superior bound related to minimal/maximal number of
        resources to bind. Used only if multiple is True.
    - proxy selection, execution and result selection in case of not multiple.

    While interfaces and proxies are internal to the port, resources and
    bindings are bound to the port because they are seen such as port
    functional properties.
    """

    class PortError(Exception):
        """Raised if new port port is inconsistent with port requirements.
        """
        pass

    INPUT = 1 << 0  #: input port kind
    OUTPUT = 1 << 1  #: output port kind
    DEFAULT_IOKIND = INPUT | OUTPUT  #: default port kind

    ITFS = '_itfs'  #: interfaces attribute name
    PROXY = '_proxy'  #: proxy attribute name
    IOKIND = '_iokind'  #: i/o kind of port (input/output/both)
    MULTIPLE = '_multiple'  #: multiple port proxy attribute name
    INF = 'inf'  #: minimal number of bindable resources attribute name
    SUP = 'sup'  #: maximal number of bindable resources attribute name
    RESOURCE = '_resource'  #: resource attribute name
    POLICYRULES = '_policyrules'  #: policy rules attribute name

    def __init__(
            self, itfs=None, resource=None, iokind=DEFAULT_IOKIND,
            multiple=True, inf=0, sup=maxint, policyrules=None,
            *args, **kwargs
    ):
        """
        :param itfs: interface(s) which describe this port.
        :type itfs: Interface or list
        :param resource: resource to proxify.
        :param int iokind: i/o kind of ports among Port.OUTPUT, Port.INPUT or
            both (default).
        :param bool multiple: multiple proxy cardinality. False by default.
        :param int inf: minimal port number to use. Default 0.
        :param int sup: maximal port number to use. Default infinity.
        :param b3j0f.rcm.io.policy.PolicyRules policyrules: policy rules.
        """

        # set private attributes
        self._resource = resource
        self._proxy = None
        self._itfs = itfs
        self._iokind = iokind
        self._multiple = multiple
        self._inf = inf
        self._sup = sup
        self._policyrules = policyrules

        super(Port, self).__init__(*args, **kwargs)

    @property
    def isoutput(self):
        """True iif this is a component output.

        :return: True iif this is a component output.
        :rtype: bool
        """

        return self._iokind & Port.OUTPUT

    @property
    def isinput(self):
        """True iif this is a component input.

        :return: True iif this is a component input.
        :rtype: bool
        """

        return self._iokind & Port.INPUT

    @property
    def iokind(self):
        """Get this i/o kind.

        :return: this i/o kind.
        :rtype: int
        """

        return self._iokind

    @iokind.setter
    def iokind(self, value):
        """Change of i/o kind.

        :param int value: new i/o kind to use.
        """

        return self._set_iokind(value)

    def _set_iokind(self, iokind):
        """Change of i/o kind.

        :param int iokind: new i/o kind to use.
        """

        self._iokind = iokind

    @property
    def multiple(self):
        """Get self multiple value.

        :return: self multiple flag.
        :rtype: bool
        """

        return self._multiple

    @multiple.setter
    def multiple(self, value):
        """Change of self multiple value.

        :param bool value: new multiple value to use.
        """

        if value != self._multiple:
            self._multiple = not self._multiple

            self._renewproxy()

    @property
    def itfs(self):
        """This interfaces.

        :return: self interfaces.
        :rtype: list
        """
        return self._itfs

    @itfs.setter
    def itfs(self, value):
        """Change of itfs.

        :param list itfs: list of interfaces to use.
        """

        self._set_itfs(itfs=value)

    def _set_itfs(self, itfs):
        """Change of itfs.

        :param list itfs: list of interfaces to use.
        """

        self._itfs = itfs

        self._renewproxy()

    @property
    def inf(self):
        """Get inferior bound property.

        :return: this inferior bound.
        """

        return self._inf

    @inf.setter
    def inf(self, value):
        """Change of lower bound property.

        :param int value: new lower bound to use.
        """

        self._inf = value

        self._renewproxy()

    @property
    def sup(self):
        """Get superior bound property.

        :return: this superior bound.
        """

        return self._sup

    @sup.setter
    def sup(self, value):
        """Change of superior bound property.

        :param int value: new superior bound to use.
        """

        self._sup = value

        self._renewproxy()

    @property
    def resources(self):
        """Get resources by port name or self if resource is this external
        resource.

        :return: self resources.
        :rtype: dict
        """

        return self._get_resources()

    def _get_resources(self):
        """Get resources by name or by self if resource is this private
        resource.

        :return: self resources.
        :rtype: dict
        """

        # defaul result is self ports
        result = Port.GET_PORTS(component=self)

        # add resource
        resource = self._resource
        if resource is not None:
            result[self.uid] = resource

        return result

    @property
    def resource(self):
        """Get resource.
        :return: this resource.
        """

        return self._resource

    @resource.setter
    def resource(self, value):
        """Change of resource.

        :param value: new resource to use.
        """

        result = self._set_resource(value)

        return result

    def _set_resource(self, resource):
        """Change of resource.

        :param value: new resource to use.
        """

        # renew resource only if input resource is not the actual resource
        if resource is not self._resource:
            self._resource = resource
            self._renewproxy()

    @property
    def proxy(self):
        """Get port proxy.

        :return: self proxy.
        """

        # result is private self _get_proxy result
        result = self._get_proxy()

        return result

    def _get_proxy(self):
        """Get port proxy.

        :return: self proxy.
        """

        # renew self _proxy if necessary
        if self._proxy is None:
            self._renewproxy()
        # return self proxy
        result = self._proxy

        return result

    def set_port(self, port, name=None, *args, **kwargs):

        # check port before binding it to self ports
        if (
                isinstance(port, Port)
                and not self.check_resource(port=port)
        ):
            # and raise related error
            raise Port.PortError(
                "Port {0} does not validate requirements {1}."
                .format(port, self.itfs)
            )
        # bind the port to self
        name, oldport = super(Port, self).set_port(
            port=port, name=name, *args, **kwargs
        )
        result = name, oldport

        # if resources have changed
        if isinstance(oldport, Port) or isinstance(port, Port):
            # renew proxy with a possible chance of raising a PortError
            self._renewproxy()

        return result

    def check_resource(self, port):
        """Check input port related to self interfaces and self.

        :param Port port: port to check. Can not be self.
        """

        resources = self.resources
        # check if maximal number of resources have not been acquired
        # and port is not self
        result = port is not self and len(resources) < self.sup

        if result and self.itfs:  # check all port itfs if they exist
            for selfitf in self.itfs:
                if port.itfs:
                    for resourceitf in port.itfs:
                        result = resourceitf.is_sub_itf(selfitf)
                        if not result:
                            break
                else:
                    result = issubclass(object, selfitf.pycls)
                    if not result:
                        break

        return result

    def _renewproxy(self):
        """Renew self proxy and propagate new proxies to all ``rports`` ports.

        :raises: Port.PortError if resources do not match inf/sup conditions.
        """

        # nonify proxy in case of errors are raised
        self._proxy = None

        # get resources
        resources = self.resources

        # check number of resources
        if len(resources) < self.inf or self.sup < len(resources):
            raise Port.PortError(
                "Number of resources: {0}. [{1}; {2}] expected in {3}.".format(
                    len(resources), self.inf, self.sup, self.uid
                )
            )

        # get the port proxy and save it in memory
        self._proxy = getportproxy(port=self)

        # and propagate changes to reversed ports
        for component in list(self._rports):
            if component is not self and isinstance(component, Port):
                bound_names = self._rports[component]
                for bound_name in list(bound_names):
                    # in this way, bound on ports will use new self proxies
                    try:
                        component.set_port(name=bound_name, port=self)
                    except Exception:
                        pass  # in catching silently bind errors

    @classmethod
    def INPUTS(cls, component, names=None, select=lambda *p: True):
        """Get input ports.

        :param type cls: port type.
        :param Component component: component from where get input ports.
        :param names: port names.
        :type names: str or list
        :param select: boolean selection function which takes a name and a port
        in parameters. True by default.
        :return: found input ports by name.
        :rtype: dict
        """

        return cls.GET_PORTS(
            component=component, names=names,
            select=lambda n, p: p.isinput and select(n, p)
        )

    @classmethod
    def OUTPUTS(cls, component, names=None, select=lambda *p: True):
        """Get output ports.

        :param type cls: port type.
        :param Component component: component from where get output ports.
        :param names: port names.
        :type names: str or list
        :param select: boolean selection function which takes a name and a port
        in parameters. True by default.
        :return: found output ports by name.
        :rtype: dict
        """

        return cls.GET_PORTS(
            component=component, names=names,
            select=lambda n, p: p.isoutput and select(n, p)
        )
