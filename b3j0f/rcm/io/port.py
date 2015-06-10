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
from b3j0f.rcm.io.core import Resource
from b3j0f.rcm.io.policy import PolicyResultSet


class Port(Resource):
    """Component port which permits to proxify component resources and to
    separate the mean to consume/provide resources from resources.

    A Port uses:

    - a input/output port kind.
    - resource(s) to proxify.
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
        """Raised if new port resource is inconsistent with port requirements.
        """
        pass

    INPUT = 1 << 0  #: input port kind
    OUTPUT = 1 << 1  #: output port kind
    DEFAULT_IOKIND = INPUT | OUTPUT  #: default port kind

    IOKIND = '_iokind'  #: i/o kind of port (input/output/both)
    MULTIPLE = '_multiple'  #: multiple resource proxy attribute name
    INF = 'inf'  #: minimal number of bindable resources attribute name
    SUP = 'sup'  #: maximal number of bindable resources attribute name
    _PROXY = '_proxy'  #: private proxies attribute name
    _SELECTPOLICY = '_selectpolicy'  #: proxy selection policy attr name
    _EXECPOLICY = '_execpolicy'  #: proxy execution policy attribute name
    _RESULTPOLICY = '_resultpolicy'  #: proxy result selection policy attr name

    def __init__(
        self,
        iokind=DEFAULT_IOKIND, multiple=True, inf=0, sup=maxsize,
        selectpolicy=None, execpolicy=None, respolicy=None,
        *args, **kwargs
    ):
        """
        :param int iokind: i/o kind of ports among Port.OUTPUT, Port.INPUT or
            both (default).
        :param bool multiple: multiple proxy cardinality. False by default.
        :param int inf: minimal proxy number to use. Default 0.
        :param int sup: maximal proxy number to use. Default infinity.
        :param selectpolicy: in case of not multiple port, a selectpolicy
            choose at runtime which proxy method to run. If it is a dict, keys
            are method names and values are callable selectpolicy. Every
            selectpolicy takes in parameters:
            - port: self port,
            - resources: self resources,
            - proxies: list of proxies to execute,
            - name: the called method name,
            - instance: the proxy instance,
            - args: method args,
            - kwargs: method kwargs.
        :type selectpolicy: dict or callable
        :param execpolicy: in case of not multiple port, a execpolicy choose at
            runtime how to execute a proxy method. If it is a dict, keys are
            method names and values are callable execpolicy. Every execpolicy
            takes in parameters:
            - port: self port,
            - resources: self resources,
            - proxies: list of proxies to execute,
            - name: the called method name,
            - instance: the proxy instance,
            - args: method args,
            - kwargs: method kwargs.
        :type selectpolicy: dict or callable
        :param respolicy: in case of not multiple port, a respolicy choose at
            which proxy method result to return. If it is a dict, keys are
            method names and values are callable respolicy. Every respolicy
            takes in parameters:
            - port: self port,
            - resources: self resources,
            - proxies: list of proxies to execute,
            - name: the called method name,
            - instance: the proxy instance,
            - args: method args,
            - kwargs: method kwargs,
            - results: method results.
        :type respolicy: dict or callable
        """

        super(Port, self).__init__(*args, **kwargs)

        # set private attributes
        self._iokind = iokind
        self._multiple = multiple
        self._inf = inf
        self._sup = sup
        self._selectpolicy = selectpolicy
        self._execpolicy = execpolicy
        self._resultpolicy = respolicy

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

    def _set_itfs(self, itfs):

        super(Port, self)._set_itfs(itfs)

        self._renewproxy()

    @property
    def inf(self):

        return self._inf

    @inf.setter
    def inf(self, value):

        self._inf = value

        self._renewproxy()

    @property
    def sup(self):

        return self._sup

    @sup.setter
    def sup(self, value):

        self._sup = value

        self._renewproxy()

    def get_resources(self):
        """Get resources by name.

        :return: self resources.
        :rtype: dict
        """

        result = self.get_ports(types=Resource)

        return result

    def _get_proxy(self, *args, **kwargs):

        # renew self _proxy if necessary
        if self._proxy is None:
            self._renewproxy()
        # return self proxy
        result = self._proxy

        return result

    def set_port(self, port, name=None, *args, **kwargs):

        # check port before binding it to self ports
        if (
            isinstance(port, Resource)
            and not self.check_resource(resource=port)
        ):
            # and raise related error
            raise Port.PortError(
                "Resource {0} does not validate requirements {1}."
                .format(port, self.itfs)
            )
        # bind the port to self
        name, oldport = super(Port, self).set_port(
            port=port, name=name, *args, **kwargs
        )
        result = name, oldport

        # if resources have changed
        if isinstance(oldport, Resource) or isinstance(port, Resource):
            # renew proxy with a possible chance of raising a PortError
            self._renewproxy()

        return result

    def check_resource(self, resource):
        """Check input resource related to self interfaces.

        :param Resource resource: resource to check.
        """

        # check if maximal number of resources have not been acquired
        result = len(self.get_resources()) < self.sup

        if result:  # check all resource itfs
            for selfitf in self.itfs:
                for resourceitf in resource.itfs:
                    result = resourceitf.is_sub_itf(selfitf)
                    if not result:
                        break

        return result

    def _renewproxy(self):
        """Renew self proxy and propagate new proxies to all ``boundon``
        ports.

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
        else:  # use one object which propagates methods to resource proxies
            if not resources:  # do nothing if resources is empty
                self._proxy = None
            else:
                proxies = []  # get a list of proxies
                for resource_name in resources:
                    resource = resources[resource_name]
                    proxy = resource.proxy
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
                            rountine=routine, proxies=proxies,
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

        # get the rights selectpolicy and execpolicy
        if isinstance(self._selectpolicy, dict):
            selectpolicy = self._selectpolicy.get(rname)
        else:
            selectpolicy = self._selectpolicy
        if isinstance(self._execpolicy, dict):
            execpolicy = self._execpolicy.get(rname)
        else:
            execpolicy = self._execpolicy
        if isinstance(self._respolicy, dict):
            respolicy = self._respolicy.get(rname)
        else:
            respolicy = self._respolicy

        # wraps the rountine
        @wraps(routine)
        def result(proxyinstance, *args, **kwargs):
            # check if proxies have to change dynamically
            if selectpolicy is None:
                proxiestorun = proxies
            else:
                proxiestorun = selectpolicy(
                    port=self, proxies=proxies, routine=rname,
                    instance=proxyinstance,
                    args=args, kwargs=kwargs
                )
            # if execpolicy is None, process proxies
            if execpolicy is None:
                results = []
                for proxy_to_run in proxiestorun:
                    rountine = getattr(proxy_to_run, rname)
                    method_res = rountine(*args, **kwargs)
                    results.append(method_res)
            else:  # if execpolicy is asked
                results = execpolicy(
                    port=self, proxies=proxiestorun,
                    routine=rname, instance=proxyinstance,
                    args=args, kwargs=kwargs
                )
            if respolicy is None:
                if (
                    isinstance(results, PolicyResultSet)
                    and results
                ):
                    result = [0]
                else:
                    result = results
            else:
                result = respolicy(
                    port=self, proxies=proxies,
                    routine=rname, instance=proxyinstance,
                    args=args, kwargs=kwargs,
                    results=results
                )
            return result

        return result


class ProxySet(tuple):
    """Associate a port proxy list with related resource names in order to
    easily choose proxies depending on resource names.

    It uses a port, port resources by name and a list of proxies.
    The get_resource_name(proxy) permits to find back proxy resource name.

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
        :param dict resources: list of resource elements by name to proxify.
        :param tuple bases: port interface pycls.
        """

        _resource_names_by_proxy = {}

        for name in resources:
            resource = resources[name]
            # do something only if resource != port
            if resource is not port:
                proxy = resource.proxy
                # ensure proxy is an Iterable
                if not isinstance(proxy, ProxySet):
                    proxy = (proxy,)
                # generate a proxy for all resource proxy
                for p in proxy:
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
        :param dict resources: list of resource elements by name to proxify.
        :param tuple bases: port interface pycls.
        """

        self.port = port
        self.resources = resources
        self.bases = bases

    def get_resource_name(self, proxy):
        """Get proxy resource name.

        :param proxy: proxy from where get resource name.
        :return: corresponding proxy resource name.
        :rtype: str
        """
        try:
            result = self._resource_names_by_proxy[proxy]
        except TypeError:
            result = self._resource_names_by_proxy[id(proxy)]

        return result
