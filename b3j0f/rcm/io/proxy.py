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

"""This module provides the mechanism to generate a port proxy thanks to the
ProxySet.get_proxy static method.
"""

__all__ = ['getportproxy', 'ProxySet', '_methodproxy']

from functools import wraps

from inspect import getmembers, isroutine

from b3j0f.utils.iterable import first
from b3j0f.utils.proxy import get_proxy
from b3j0f.rcm.io.policy.core import PolicyResultSet


class ProxySet(tuple):
    """Associate a port proxy list with related port names in order to
    easily choose proxies depending on port names.

    It uses a port, port resources by name and a list of proxies.
    The resource_name(proxy) permits to find back proxy port name.

    It inherits from a tuple in order avoid modification.
    """

    PORT = 'port'  #: port attribute name
    RESOURCES = 'resources'  #: resources attribute name
    BASES = 'bases'  #: port interface types

    #: private proxies by name attribute name
    _RESOURCE_NAMES_BY_PROXY = '_resource_names_by_proxy_pos'

    def __new__(cls, port, resources, bases):
        """
        :param Port port: resources port.
        :param dict resources: list of port elements by name to proxify.
        :param tuple bases: port interface pycls.
        """

        _resource_names_by_proxy_pos = {}

        proxies = []

        # get proxies of resources
        for name in resources:
            resource = resources[name]
            resourceproxies = getattr(resource, 'proxy', resource)
            # ensure proxies is an Iterable
            if not isinstance(resourceproxies, ProxySet):
                resourceproxies = (resourceproxies,)

            # generate a proxy for all port proxies
            for proxy in resourceproxies:
                new_proxy = get_proxy(elt=proxy, bases=bases)
                proxies.append(new_proxy)
                # and save names in _resource_names_by_proxy_pos
                _resource_names_by_proxy_pos[len(proxies) - 1] = name

        # get result from super constructor
        result = super(ProxySet, cls).__new__(cls, proxies)
        result._resource_names_by_proxy_pos = _resource_names_by_proxy_pos

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

    def resource_name(self, pos):
        """Get resource name from a proxy pos.

        :param pos: proxy position in proxies list.
        :return: corresponding proxy port name.
        :rtype: str
        """

        result = self._resource_names_by_proxy_pos[pos]

        return result

    def proxies_pos(self, name):
        """Get positions of proxies from a resource name.

        :param str name: resource name from where get proxies.
        :return:
        :rtype: list
        """

        result = []

        for pos in self._resource_names_by_proxy_pos:
            resource_name = self._resource_names_by_proxy_pos[pos]

            if resource_name == name:
                result.append(pos)

        return result


def getportproxy(port, protected=False):
    """Get port proxy.

    :param b3j0f.rcm.io.port.Port port: port from which get proxy.
    :param bool protected: also proxify protected methods if True (False by
        default).
    :return: proxy port related to port resources.
    """

    result = None

    # get bases interfaces
    bases = (object, ) if port.itfs is None else (
        itf.pycls for itf in port.itfs
    )

    resources = port.resources

    # if multiple, proxies is a ProxySet
    if port.multiple:
        result = ProxySet(port=port, resources=resources, bases=bases)

    # use one object which propagates methods to port proxies
    elif resources:
        proxies = []  # get a list of proxies

        for rname in resources:
            # get subport
            subport = resources[rname]
            # if rname is not port, use directly subport
            proxy = subport if rname is port else subport.proxy

            # if proxy is a proxy set, add items
            if isinstance(proxy, ProxySet):
                proxies += proxy

            else:
                proxies.append(proxy)

        # embed proxies in a policy result set for future policy executions
        proxies = PolicyResultSet(proxies)
        _dict = {}  # proxy dict to fill with dedicated methods
        # wraps all interface methods
        for base in bases:
            # among public members
            for rname, routine in getmembers(
                    base,
                    lambda mname, member:
                    (protected or mname[0] != '_')  # filter public methods
                    and isroutine(member)  # get only routine
                    and mname not in _dict  # avoid already proxified elts
            ):
                # get related method proxy
                methodproxy = _methodproxy(
                    port=port, routine=routine, proxies=proxies,
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
        result = get_proxy(elt=proxy, bases=bases, _dict=_dict)

    return result


def _methodproxy(port, routine, rname, proxies):
    """Generate a routine proxy related to input routine, routine name and
    a list of proxies.

    :param routine: routine to proxify.
    :param str rname: routine name.
    :param PolicyResultSet proxies: proxies to proxify.
    :return: routine proxy.
    """

    # wraps the routine
    @wraps(routine)
    def result(proxyinstance, *args, **kwargs):
        """Proxy selection wraper.
        """

        # execute policies on proxies
        proxiestorun = port._policyset.execute(
            port=port, proxies=proxies, routine=rname,
            instance=proxyinstance, args=args, kwargs=kwargs
        )

        if port.multiple:  # if port is multiple, execute all proxies
            # get the right result
            result = []

            for proxy in proxiestorun:
                routine = getattr(proxy, rname)
                method_res = routine(*args, **kwargs)
                result.append(method_res)

        else:  # if not multiple, execute the first proxiestorun
            proxy = first(proxiestorun)
            if proxy is not None:
                routine = getattr(proxy, rname)
                result = routine(*args, **kwargs)

        return result

    return result
