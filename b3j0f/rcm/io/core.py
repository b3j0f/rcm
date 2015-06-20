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

__all__ = ['Port', 'ProxySet']

from inspect import getmembers, isroutine

from functools import wraps

from sys import maxsize

from b3j0f.utils.proxy import get_proxy
from b3j0f.rcm.io.policy import PolicyResultSet
from b3j0f.rcm.ctrl.core import Controller


class Port(Controller):
    """Controller which implements the proxy design pattern in order
    to separate component business realization from its consumption/providing.

    A Port uses:

    - interfaces such as port provided/consumed description.
    - a proxified resource.
    - input/output port kind(s).
    - bound port(s) to proxify.
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
    _PROXY = '_proxy'  #: private proxies attribute name
    POLICYRULES = '_policyrules'  #: policy rules attribute name

    def __init__(
            self, itfs=None, proxy=None,
            iokind=DEFAULT_IOKIND, multiple=True, inf=0, sup=maxsize,
            policyrules=None,
            *args, **kwargs
    ):
        """
        :param itfs: interface(s) which describe this port.
        :type itfs: Interface or list
        :param proxy: default port proxy.
        :param int iokind: i/o kind of ports among Port.OUTPUT, Port.INPUT or
            both (default).
        :param bool multiple: multiple proxy cardinality. False by default.
        :param int inf: minimal port number to use. Default 0.
        :param int sup: maximal port number to use. Default infinity.
        :param b3j0f.rcm.io.policy.PolicyRules policyrules: policy rules.
        """

        super(Port, self).__init__(*args, **kwargs)

        # set private attributes
        self._proxy = proxy
        self._itfs = itfs
        self._iokind = iokind
        self._multiple = multiple
        self._inf = inf
        self._sup = sup
        self._policyrules = policyrules

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

    def get_resources(self):
        """Get resources by name.

        :return: self resources.
        :rtype: dict
        """

        result = Port.GET_PORTS(component=self)

        return result

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
        """Check input port related to self interfaces.

        :param Port port: port to check.
        """

        # check if maximal number of resources have not been acquired
        result = len(self.get_resources()) < self.sup

        if result and self.itfs:  # check all port itfs if they exist
            for selfitf in self.itfs:
                for resourceitf in port.itfs:
                    result = resourceitf.is_sub_itf(selfitf)
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
        resources = self.get_resources()

        # check number of resources
        if len(resources) < self.inf or self.sup < len(resources):
            raise Port.PortError(
                "Number of resources: {0}. [{1}; {2}] expected in {3}.".format(
                    len(resources), self.inf, self.sup, self.uid
                )
            )
        # get bases interfaces
        bases = (itf.pycls for itf in self.itfs)

        # if multiple, proxies is a ProxySet
        if self.multiple:
            self._proxy = ProxySet(
                port=self, resources=resources, bases=bases
            )
        else:  # use one object which propagates methods to port proxies
            if not resources:  # do nothing if resources is empty
                self._proxy = None
            else:
                proxies = []  # get a list of proxies
                for resource_name in resources:
                    port = resources[resource_name]
                    proxy = port.proxy
                    if isinstance(proxy, ProxySet):
                        proxies += proxy
                    else:
                        proxies.append(proxy)
                # embed proxies in a policy result set for future policies
                proxies = PolicyResultSet(proxies)
                _dict = {}  # proxy dict to fill with dedicated methods
                # wraps all interface methods
                for base in bases:
                    # among public members
                    for rname, routine in getmembers(
                            base,
                            lambda mname, member:
                            mname[0] != '_' and isroutine(member)
                    ):
                        # get related method proxy
                        methodproxy = self._methodproxy(
                            routine=routine, proxies=proxies,
                            rname=rname
                        )
                        # update _dict with method proxy
                        _dict[rname] = methodproxy

                # add default constructor
                _dict['__new__'] = _dict['__init__'] = (
                    lambda *args, **kwargs: None
                )
                # get proxy elt
                proxycls = type('Proxy', bases, _dict)
                proxy = proxycls()
                # generate a dedicated proxy which respects method signatures
                self._proxy = get_proxy(elt=proxy, bases=bases, _dict=_dict)

        # and propagate changes to reversed ports
        for component in list(self._rports):
            if component is not self and isinstance(component, Port):
                bound_names = self._rports[component]
                for bound_name in list(bound_names):
                    # in this way, bound on ports will use new self proxies
                    try:
                        component[bound_name] = self
                    except Exception:
                        pass  # in catching silently bind errors

    def _methodproxy(self, routine, rname, proxies):
        """Generate a routine proxy related to input routine, routine name and
        a list of proxies.

        :param routine: routine to proxify.
        :param str rname: routine name.
        :param PolicyResultSet proxies: proxies to proxify.
        :return: routine proxy.
        """

        # get the rights policy rules
        selectpr = self._policyrules.selectpr(rname)
        execpr = self._policyrules.exectpr(rname)
        resultpr = self._policyrules.resultpr(rname)

        # wraps the routine
        @wraps(routine)
        def result(proxyinstance, *args, **kwargs):
            """Proxy selection wraper.
            """

            # check if proxies have to change dynamically
            if selectpr is None:
                proxiestorun = proxies
            else:
                proxiestorun = selectpr(
                    port=self, proxies=proxies, routine=rname,
                    instance=proxyinstance,
                    args=args, kwargs=kwargs
                )
            # if execpr is None, process proxies
            if execpr is None:
                results = []
                for proxy_to_run in proxiestorun:
                    rountine = getattr(proxy_to_run, rname)
                    method_res = rountine(*args, **kwargs)
                    results.append(method_res)
            else:  # if execpr is asked
                results = execpr(
                    port=self, proxies=proxiestorun,
                    routine=rname, instance=proxyinstance,
                    args=args, kwargs=kwargs
                )
            if resultpr is None:
                if (
                        isinstance(results, PolicyResultSet)
                        and results
                ):
                    result = [0]
                else:
                    result = results
            else:
                result = resultpr(
                    port=self, proxies=proxies,
                    routine=rname, instance=proxyinstance,
                    args=args, kwargs=kwargs,
                    results=results
                )
            return result

        return result


class ProxySet(tuple):
    """Associate a port proxy list with related port names in order to
    easily choose proxies depending on port names.

    It uses a port, port resources by name and a list of proxies.
    The get_resource_name(proxy) permits to find back proxy port name.

    It inherits from a tuple in order avoid modification.
    """

    PORT = 'port'  #: port attribute name
    RESOURCES = 'resources'  #: resources attribute name
    BASES = 'bases'  #: port interface types

    #: private proxies by name attribute name
    _RESOURCE_NAMES_BY_PROXY = '_resource_names_by_proxy'

    def __new__(cls, port, resources, bases):
        """
        :param Port port: resources port.
        :param dict resources: list of port elements by name to proxify.
        :param tuple bases: port interface pycls.
        """

        _resource_names_by_proxy = {}

        for name in resources:
            port = resources[name]
            # do something only if port != port
            if port is not port:
                proxies = port.proxy
                # ensure proxies is an Iterable
                if not isinstance(proxies, ProxySet):
                    proxies = (proxies,)
                # generate a proxy for all port proxies
                for proxy in proxies:
                    new_proxy = get_proxy(elt=proxy, bases=bases)
                    # and save names in _resource_names_by_proxy
                    try:
                        _resource_names_by_proxy[new_proxy] = name

                    except TypeError:
                        _resource_names_by_proxy[id(new_proxy)] = name

        result = super(ProxySet, cls).__new__(
            cls, _resource_names_by_proxy.keys()
        )
        result._resource_names_by_proxy = _resource_names_by_proxy

        return result

    def __init__(self, port, resources, bases):
        """
        :param Port port: resources port.
        :param dict resources: list of port elements by name to proxify.
        :param tuple bases: port interface pycls.
        """

        super(ProxySet, self).__init__()

        self.port = port
        self.resources = resources
        self.bases = bases

    def get_resource_name(self, proxy):
        """Get proxy port name.

        :param proxy: proxy from where get port name.
        :return: corresponding proxy port name.
        :rtype: str
        """

        try:
            result = self._resource_names_by_proxy[proxy]

        except TypeError:
            result = self._resource_names_by_proxy[id(proxy)]

        return result
