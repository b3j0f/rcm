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

"""This module provides classes in charge of executing proxy resource
selection policy.

Policies are dedicated to select proxy resources from a port.

Default policy values are:

- One: select the first resource.
- All: select all resources.
- RoundAbout: select iteratively a resource among resources. The first call
select the first resource. Second call, the second. When all resources have
been called once, the policy starts again with the first resource.
- Random: select random resources.
- OneRandom: select one random resource.
- BestEffort: select the first resource which does not raise an Error.
- Count: select a number of resources between min and max value.
- Aggregate: use one proxy which delegates its method execution to all input
resource proxies.
- Dynamic: select resources which are checked by a function filter.
"""

__all__ = [
    'Policy',
    'OnePolicy', 'AllPolicy', 'DynamicPolicy',
    'RoundAboutPolicy', 'RandomPolicy', 'OneRandomPolicy',
    'BestEffortPolicy', 'aggregate', 'select_proxies'
]

from random import randint

from inspect import getmembers, isroutine

from collections import Iterable

from functools import wraps

from b3j0f.utils.proxy import get_proxy
from b3j0f.utils.path import lookup
from b3j0f.utils.iterable import first


def select_proxies(port, proxies, select=None, *args, **kwargs):
    """Implement the port proxy policy with a parametrable selection.

    :param Port port: default port proxies.
    :param list proxies: list of proxy elements to proxify.
    :param select: callable which takes in parameters a port and
        proxies and returns proxies.
    :return: proxy selection.
    :rtype: object or list
    """

    # default result is None
    result = None
    # get bases from port interfaces
    interfaces = port.interfaces
    bases = (interface.pvalue for interface in interfaces)
    # if select exists, use it to select proxies to keep
    if select is not None:
        proxies = select(port=port, proxies=proxies)
    # generate proxies related to selected proxies
    if isinstance(proxies, Iterable):
        result = []
        for proxy in proxies:
            new_proxy = get_proxy(elt=proxy, bases=bases)
            result.append(new_proxy)
    elif proxies is not None:  # generate one proxy
        result = get_proxy(elt=proxies, bases=bases)

    return result


def aggregate(
    port, proxies, initselect=None, dynselect=None, dynexec=None,
    *args, **kwargs
):
    """Implement the port proxy policy with a parametrable selection and
    returns a proxy where all methods process all proxy selection methods.

    :param Port port: default port proxies.
    :param list proxies: list of proxy elements to proxify.
    :param initselect: proxy selection function which is executed at
        initialization.
    :param dynselect: proxy selection function which is executed at each
        proxy method execution. Takes in parameters the port, the proxies,
        the method name, the instance, args and kwargs of the method call.
    :param dynexec: dynamic proxy execution. Takes in parameters the port, the
        proxies, the method name, the instance, args and kwargs of the method
        call.
    :param selection: selection function which takes in
    :return: proxy selection.
    """
    # get proxies selection
    proxies = select_proxies(
        port=port, proxies=proxies, select=initselect, *args, **kwargs
    )
    # get interfaces, bases and _dict for proxy generation
    interfaces = port.interfaces
    bases = (interface.pvalue for interface in interfaces)
    _dict = {}
    # wraps all interface methods
    for interface in interfaces:
        pvalue = interface.pvalue
        # among public members
        for name, member in getmembers(
            pvalue, lambda name, member: name[0] != '_' and isroutine(member)
        ):
            # wraps the member
            @wraps(member)
            def method_proxy(proxy_instance, *args, **kwargs):
                # check if proxies have to change dynamically
                if dynselect is not None:
                    proxies_to_run = dynselect(
                        port=port, proxies=proxies, name=name,
                        instance=proxy_instance, args=args, kwargs=kwargs
                    )
                else:
                    proxies_to_run = proxies

                # if dynexec is None, process proxies
                if dynexec is None:
                    # result depends on proxies
                    if isinstance(proxies_to_run, Iterable):
                        # in case of iterable, get all results in a dictionary
                        result = {}
                        for proxy_to_run in proxies_to_run:
                            method = getattr(proxy_to_run, name)
                            method_result = method(*args, **kwargs)
                            result[id(proxy_to_run)] = method_result
                    else:
                        # else, proxies is a proxy and result is method exec
                        method = getattr(proxies_to_run, name)
                        result = method(*args, **kwargs)
                else:  # if dynexec is asked
                    result = dynexec(
                        port=port, proxies=proxies, name=name,
                        instance=proxy_instance, args=args, kwargs=kwargs
                    )

                return result

            # update _dict with method proxy
            _dict[name] = method_proxy
        # add default constructor
        _dict['__init__'] = lambda *args, **kwargs: None

    # get proxy elt
    elt = type('Proxy', bases, _dict)()
    # generate a dedicated proxy which respects method signatures
    result = get_proxy(elt=elt, bases=bases, _dict=_dict)

    return result


def get_policy(name, path=None):
    """Get policy class.

    >>> get_policy(name='all').__name__
    b3j0f.rcm.controller.policy.AllPolicy.

    :param str name: policy name. Related class name must finish by 'Policy'.
    :param str path: policy class module. If None, use __file__ path.
    :return: Policy class.
    :rtype: type
    """

    if path is None:
        path = __file__[:-3]

    full_name = "{0}.{1}Policy".format(path, name.capitalize())

    result = lookup(full_name)

    return result


class Policy(object):
    """Proxy resource selection policy.
    """

    def __init__(self, conf=None):
        """
        :param dict conf: policy configuration.
        """

        super(Policy, self).__init__()

        self.conf = conf

    def __call__(self, port, proxies):
        """Select proxies.

        :param Port port: proxiers port.
        :param list proxies: list of proxies to select.
        """

        raise NotImplementedError()


class DynamicPolicy(Policy):
    """Dynamic policy.
    """

    def __init__(
        self, initselect=None, dynselect=None, dynexec=None, *args, **kwargs
    ):

        super(DynamicPolicy, self).__init__(*args, **kwargs)

        self.initselect = initselect
        self.dynselect = dynselect
        self.dynexec = dynexec

    def __call__(self, port, proxies, *args, **kwargs):

        result = aggregate(
            port=port, proxies=proxies,
            initselect=self.initselect, dynselect=self.dynselect,
            dynexec=self.dynexec
        )

        return result


class OnePolicy(Policy):
    """One policy resource policy.

    Select first resource or None if sources is empty.
    """

    def __call__(self, port, proxies, *args, **kwargs):

        result = select_proxies(
            port=port, proxies=proxies, select=first(proxies)
        )
        return result


class AllPolicy(Policy):
    """All proxy resource policy.

    Select all resources.
    """

    def __call__(self, port, proxies, *args, **kwargs):

        result = select_proxies(port=port, proxies=proxies)

        return result


class RandomPolicy(Policy):
    """One Random proxy resource policy.

    Select one random proxy or None if sources is empty.
    """

    COUNT = 'count'  #: count configuration

    def __call__(self, port, proxies, *args, **kwargs):

        def dynselect(port, proxies):
            count = self.conf.get('count')

            result = list(proxies)

            for i in range(max(0, len(proxies) - count)):
                index_to_pop = randint(0, len(result))
                result.pop(index_to_pop)

            return result

        result = aggregate(port=port, proxies=proxies, dynselect=dynselect)

        return result


class OneRandomPolicy(Policy):
    """One Random proxy resource policy.

    Select one random proxy or None if sources is empty.
    """

    def __call__(self, port, proxies, *args, **kwargs):

        def dynselect(port, proxies):

            if proxies:
                result = proxies[randint(0, len(proxies))]
            else:
                result = None

            return result

        result = aggregate(port=port, proxies=proxies, dynselect=dynselect)

        return result


class RoundAboutPolicy(Policy):
    """Round about proxy resource policy.

    Select iteratively resources or None if sources is empty.
    """

    def __init__(self, *args, **kwargs):

        super(RoundAboutPolicy, self).__init__(*args, **kwargs)

        self.index = 0

    def __call__(self, port, proxies, *args, **kwargs):

        result = None

        def dynselect(port, proxies):
            self.index = self.index + 1
            self.index %= len(proxies)
            return proxies[self.index]

        result = aggregate(
            port=port, proxies=proxies, dynselect=dynselect
        )

        return result


class BestEffortPolicy(Policy):
    """Best effort proxy resource policy.

    Select first resources which does not raise an Error, otherwise last error
        or None if no sources.
    """

    def __call__(self, port, proxies, *args, **kwargs):

        def dynexec(port, proxies, name, instance, args, kwargs):

            for proxy in proxies:
                method = getattr(proxy, name)
                try:
                    result = method(*args, **kwargs)
                except Exception:
                    pass
                else:
                    break
            return result

        result = aggregate(port=port, proxies=proxies, dynexec=dynexec)

        return result
