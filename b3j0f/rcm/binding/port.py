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
    'Port', 'ProxySet'
]

from inspect import getmembers, isroutine

from functools import wraps

from sys import maxsize

from b3j0f.utils.proxy import get_proxy
from b3j0f.rcm.binding.core import Resource


class Port(Resource):
    """Component port which permits to proxify component resources and to
    separate the mean to consume/provide resources from resources.

    A Port uses:

    - resources to proxify.
    - a multiple boolean flag which specifies port proxifier cardinality. If
        True, get_proxy returns one proxy, otherwise a tuple of proxies. False
        by default.
    - a minimal/maximal number of resources to bind. Used only if multiple is
        True.

    While interfaces and proxies are internal to the port, resources and
    bindings are bound to the port because they are seen such as port
    functional properties.
    """

    class PortError(Exception):
        """Raised if new port resource is inconsistent with port requirements.
        """

        pass

    MULTIPLE = '_multiple'  #: multiple resource proxy attribute name
    INF = 'inf'  #: minimal number of bindable resources attribute name
    SUP = 'sup'  #: maximal number of bindable resources attribute name
    _PROXY = '_proxy'  # private proxies attribute name
    _PROXIFIER = '_proxifier'  #: resource proxifier attribute name

    def __init__(
        self,
        multiple=True, inf=0, sup=maxsize, dynselect=None, dynexec=None,
        *args, **kwargs
    ):
        """
        :param bool multiple: multiple proxy cardinality. False by default.
        :param int inf: minimal proxy number to use. Default 0.
        :param int sup: maximal proxy number to use. Default infinity.
        :param dynselect: in case of not multiple port, a dynselect choose at
            runtime which proxy method to run. If it is a dict, keys are
            method names and values are callable dynselect. Every dynselect
            takes in parameters:
            - port: self port,
            - resources: self resources,
            - proxies: list of proxies to execute,
            - name: the called method name,
            - instance: the proxy instance,
            - args: method args,
            - kwargs: method kwargs.
        :type dynselect: dict or callable
        :param dynexec: in case of not multiple port, a dynselect choose at
            runtime how to execute a proxy method. If it is a dict, keys are
            method names and values are callable dynselect. Every dynselect
            takes in parameters:
            - port: self port,
            - resources: self resources,
            - proxies: list of proxies to execute,
            - name: the called method name,
            - instance: the proxy instance,
            - args: method args,
            - kwargs: method kwargs.
        :type dynselect: dict or callable
        """

        super(Port, self).__init__(*args, **kwargs)

        # set private attributes
        self._multiple = multiple
        self._inf = inf
        self._sup = sup
        self._dynselect = dynselect
        self._dynexec = dynexec
        # nonify self _proxy in order to execute self._renew_proxy asap
        self._proxy = None

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

            self._renew_proxy()

    @property
    def itfs(self):

        return self._itfs

    @itfs.setter
    def itfs(self, value):

        super(Port, self).itfs = value

        self._renew_proxy()

    @property
    def resources(self):
        """Get resources by name.

        :return: self resources.
        :rtype: dict
        """

        result = self.get_ports(types=Resource)

        return result

    @property
    def proxy(self):

        # renew self _proxy if necessary
        if self._proxy is None:
            self._renew_proxy()
        # return self proxies
        result = self._proxy

        return result

    def set_port(self, port, name=None, *args, **kwargs):

        # check port
        if isinstance(port, Resource) and not self.check_res(resource=port):
            # and raise related error
            raise Port.PortError(
                "Resource {0} does not validate requirements {1}."
                .format(port, self.itfs)
            )

        result = name, old_port = super(Port, self).set_port(
            port=port, name=name, *args, **kwargs
        )

        # boolean flag if resource change
        change_of_resources = False
        # remove old resource
        if isinstance(old_port, Resource):
            self._remove_resource(name=name, resource=old_port)
            change_of_resources = True
        # add new resource
        if isinstance(port, Resource):
            self._add_resource(name=name, resource=port)
            change_of_resources = True
        # if resources have changed
        if change_of_resources:
            # renew self proxies
            self._renew_proxy()

        return result

    def check_res(self, resource):
        """Check input resource related to self interfaces.

        :param Resource resource: resource to check.
        """
        # result equals True by default
        result = True

        # check all resource itfs
        for resource_itf in resource.itfs:
            for self_itf in self.itfs:
                result = resource_itf.is_sub_itf(self_itf)
                if not result:
                    break

        return result

    def _renew_proxy(self):
        """Renew self proxy and propagate new proxies to all ``bound_on``
        ports.
        """

        # get resources
        resources = self.resources[self.inf:self.sup]
        # get bases interfaces
        bases = (itf.py_class for itf in self.ifs)

        # if multiple, proxies is a ProxySet
        if self.multiple:
            self._proxies = ProxySet(
                port=self, resources=resources, bases=bases
            )
        else:  # use one object which propagates methods to resource proxies
            if not resources:  # do nothing if resources is empty
                self._proxies = None
            else:
                proxies = []  # get a list of proxies
                for resource_name in resources:
                    resource = resources[resource_name]
                    proxy = resource.proxy
                    if isinstance(proxy, ProxySet):
                        proxies += proxy
                    else:
                        proxies.append(proxy)
                _dict = {}  # proxy dict to fill with dedicated methods
                # get dynselect and dynexec
                dynselect = self._dynselect
                dynselectisdict = isinstance(dynselect, dict)
                dynexec = self._dynexec
                dynexecisdict = isinstance(dynexec, dict)
                # wraps all interface methods
                for base in bases:
                    # among public members
                    for name, member in getmembers(
                        base,
                        lambda name, member:
                            name[0] != '_' and isroutine(member)
                    ):
                        # get the rights dynselect and dynexec
                        if dynselectisdict:
                            _dynselect = dynselect.get(name)
                        else:
                            _dynselect = dynselect
                        if dynexecisdict:
                            _dynexec = dynexec.get(name)
                        else:
                            _dynexec = dynexec

                        # wraps the rountine
                        @wraps(member)
                        def method_proxy(proxy_instance, *args, **kwargs):
                            # check if proxies have to change dynamically
                            if _dynselect is None:
                                proxies_to_run = proxies
                            else:
                                proxies_to_run = dynselect(
                                    port=self, proxies=proxies, name=name,
                                    instance=proxy_instance,
                                    args=args, kwargs=kwargs
                                )
                            # if dynexec is None, process proxies
                            if _dynexec is None:
                                result = []
                                for proxy_to_run in proxies_to_run:
                                    method = getattr(proxy_to_run, name)
                                    method_res = method(*args, **kwargs)
                                    result.append(method_res)
                            else:  # if dynexec is asked
                                result = _dynexec(
                                    port=self, proxies=proxies, name=name,
                                    instance=proxy_instance,
                                    args=args, kwargs=kwargs
                                )

                            return result

                        # update _dict with method proxy
                        _dict[name] = method_proxy

                # add default constructor
                _dict['__new__'] = _dict['__init__'] = (
                    lambda *args, **kwargs: None
                )
                # get proxy elt
                elt = type('Proxy', bases, _dict)()
                # generate a dedicated proxy which respects method signatures
                self._proxy = get_proxy(elt=elt, bases=bases, _dict=_dict)

        # and propagate changes to "bound on" ports
        for component in self._bound_on:
            if isinstance(component, Port):
                bound_names = self._bound_on[component]
                for bound_name in bound_names:
                    # in this way, bound on ports will use new self proxies
                    component[bound_name] = self


class ProxySet(tuple):
    """Used to associate a port proxy list with related resource names in order
    to easily choose proxies depending on resource names.

    It uses a port, port resources by name and a list of proxies.
    The get_resource_name(proxy) permits to find back proxy resource name.

    It inherits from a tuple in order to avoir to usages to not modify it.
    """

    PORT = 'port'  #: port attribute name
    RESOURCES = 'resources'  #: resources attribute name

    #: private proxies by name attribute name
    _RESOURCE_NAMES_BY_PROXY = '_resource_names_by_proxy'

    def __init__(self, port, resources, bases):
        """
        :param Port port: resources port.
        :param dict resources: list of resource elements by name to proxify.
        :param dict resource_names_by_proxy: set of resoure names by proxy.
        """

        self.port = port
        self.resources = resources

        self._resource_names_by_proxy = {}

        for name in resources:
            resource = resources[name]
            proxy = resource[name]
            # ensure proxy is an Iterable
            if not isinstance(proxy, ProxySet):
                proxy = (proxy,)
            for p in proxy:
                new_proxy = get_proxy(elt=proxy, bases=bases)
                self._resource_names_by_proxy[new_proxy] = name

        super(ProxySet, self).__init__(self._resource_names_by_proxy.keys())

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
