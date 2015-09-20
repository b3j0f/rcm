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

__all__ = ['proxifyresources', 'ProxySet', '_methodproxy']

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


def proxifyresources(
        resources,
        bases=(object), oneinput=True, oneoutput=True, policyruler=None,
        protected=False
):
    """Proxify input resources related to input parameters.

    :param dict resources: resources by name to proxify.
    :param tuple bases: base classes from which get routines to proxify.
    :param bool oneinput: port one input flag.
    :param bool oneoutput: port one output flag. If True, return one instance
        which implements all base classes from the input parameter ``bases``.
        Otherwise, return a ProxySet.
    :param bool protected: if False (default) proxify only public routines
        from the base classes.
    :return: proxified resources.

        If ``oneoutput``, return one instance class which implements ``bases``
        classes and executes all resources. Otherwise, ProxySet. If oneinput,
        the proxy executes at most one resource in applying policyruler
        selection before.
    """

    if oneoutput:

        proxydict = {}

        for base in bases:
            for name, routine in getmembers(
                    base, lambda name, member:
                    name not in proxydict and
                    isroutine(member) and protected or name[0] != '_'
            ):
                @wraps(routine)
                def routineproxy(*args, **kwargs):

                    result = None  # default result

                    if policyruler is not None:
                        resources = policyruler.select(resources)

                    if oneinput:
                        for name in resources:
                            resources = {name: resources[name]}

                    for name in resources:
                        resource = resources[name]
                        resourceroutine = getattr(resource, name)

                        if policyruler is None:
                            result[name] = resourceroutine(*args, **kwargs)

                        else:
                            result[name] = policyruler.execute(
                                resourceroutine, args, kwargs
                            )

                    if oneinput:
                        result = result[name] if result else None

                    return result

                proxydict[name] = routineproxy

        result = get_proxy(bases=bases, _dict=proxydict)

    else:

        result = {}

        # get a list of all resources
        allresources = []
        for name in resources:
            resource = resources[name]

            if isinstance(resource, ProxySet):
                allresources += resource

            else:
                allresources.append(resource)

        # proxify all resources
        for resource in allresources:

            proxydict = {}

            for base in bases:
                for name, routine in getmembers(
                        base, lambda name, member:
                        isroutine(member) and protected or name[0] != '_'
                ):

                    resourceroutine = getattr(resource, name)

                    @wraps(routine)
                    def routineproxy(*args, **kwargs):

                        rr = resourceroutine

                        if policyruler is None:
                            result = rr(*args, **kwargs)

                        else:
                            result = policyruler.execute(
                                rr, args, kwargs
                            )

                        return result

                    proxydict[name] = routineproxy

            # add default constructor
            proxydict['__new__'] = proxydict['__init__'] = (
                lambda *args, **kwargs: None
            )

            proxy = get_proxy(
                elt=resourceroutine, bases=bases, _dict=proxydict
            )

        result[name] = proxy

    return result

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
                    port=port, routine=routine, proxies=proxies, rname=rname
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
