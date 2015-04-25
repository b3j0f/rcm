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
    'Binding', 'Port', 'Interface'
]

from collections import Iterable

from inspect import isclass

from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup
from b3j0f.utils.proxy import get_proxy
from b3j0f.rcm.core import Component


class Interface(object):
    """Port interface which is used to check and to generate proxy resource.

    Provides a pvalue which is the python interface corresponding to the value.
    """

    class ValueError(Exception):
        """Raised while trying to update value.
        """
        pass

    VALUE = '_value'
    PVALUE = '_pvalue'

    def __init__(self, value=None):
        """
        :param str value: value interface. Default is object.
        """

        super(Interface, self).__init__()

        self.value = value

    @property
    def value(self):
        """Get interface value.

        :return: self value.
        :rtype: str
        """

        return self._value

    @value.setter
    def value(self, value):
        """Change of value interface.

        :param str value: new value interface.
        """
        # set private value attribute
        self._value = value
        # get _pvalue
        if value is None:
            value = object
        elif isinstance(value, basestring):
            value = self._get_pvalue(value)
        # check type of value
        if isclass(value):  # update attribute only if value is a class
            self._pvalue = value
        else:  # otherwise, raise an error
            raise Interface.ValueError(
                "Wrong interface value {0}".format(value)
            )

    @property
    def pvalue(self):
        """Get python interface.

        :return: python interface.
        """

        return self._pvalue

    def _get_pvalue(self, value):
        """Protected method to override in order to get pvalue from input
        value.

        :param str value: value to convert to a python interface.
        :return: python value conversion.
        :rtype: type
        """

        try:
            result = lookup(value)
        except ImportError as ie:
            raise Interface.ValueError(ie)

        return result

    def check(self, resource, proxy):
        """Check if input proxy respects this requirements.

        :param Resource resource: proxy resource to check.
        :param proxy: proxy to check.
        :return: True if proxy respects this requirements.
        :rtype: bool
        """

        return isinstance(proxy, self._pvalue)


class Resource(object):
    """Resource element which implements the proxy design pattern in order
    to separate resource realization from its usage.
    """

    def get_proxy(self):
        """Get resource proxy.

        :return: self proxy.
        """

        raise NotImplementedError()


class Port(Component, Resource):
    """Component port which permits to proxify component resources and to
    separate the mean to consume/provide resources from resources.

    A Port uses:

    - a set of interfaces in order to filter which kind
        of resources can be bound/provided to/by a component.
    - resources to proxify.
    - proxies.
    - a set of bindings which are the mean to proxify a resource.

    While interfaces and proxies are internal to the port, resources and
    bindings are bound to the port because they are seen such as port
    functional properties.
    """

    class ResourceError(Exception):
        """Raised if new port resource is inconsistent with port requirements.
        """
        pass

    INTERFACES = '_interfaces'  #: interfaces field name
    POLICY = '_policy'  #: proxy selection policy

    def __init__(
        self,
        interfaces=None, resources=None, bindings=None, policy=None,
        *args, **kwargs
    ):
        """
        :param interfaces: Port interface names/classes.
        :type interfaces: list or str
        :param resource: resource to proxify.
        :param bindings: binding(s) to use.
        :type bindings: list or Binding
        :param policy: proxy selection policy.
        :type policy: str or function
        """

        super(Port, self).__init__(*args, **kwargs)

        # set public attributes
        self.policy = policy
        self.interfaces = interfaces
        self.bindings = bindings
        self.resources = resources

    @property
    def policy(self):
        """Get default policy.

        :return: self policy.
        :rtype: function
        """

        return self._policy

    @policy.setter
    def policy(self, value):
        """Change of policy.

        :param value: new policy to use.
        :type value: str or function
        """

        # ensure value is a function
        if isinstance(value, basestring):
            value = lookup(value)

        self._policy = value

    @property
    def resources(self):
        """Get resources by name.

        :return: self resources.
        :rtype: dict
        """

        result = self.get_ports(types=Resource)

        return result

    def set_port(self, port, name=None, *args, **kwargs):

        # check port
        if isinstance(port, Resource) and not self.check(resource=port):
            # and raise related error
            raise Port.PortError(
                "Resource {0} does not validate requirements {1}"
                .format()
            )

        name, old_port = super(Port, self).set_port(
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
            # propagate changes to bound on ports
            for component in self._bound_on:
                if isinstance(component, Port):
                    bound_names = self._bound_on[component]
                    for bound_name in bound_names:
                        component[name] = self

    def _get_proxy(self, resource):
        """Get resource proxy. Called internally by self resource setter
        property.

        :param resource: resource to proxify.
        """

        # if resource is a proxy port
        if isinstance(resource, Port):
            toproxify = resource.get_proxy()
        else:
            toproxify = resource

        # generate the right proxy/ies
        if isinstance(toproxify, Iterable):
            result = (
                get_proxy(elt=elt, bases=self.interfaces) for elt in toproxify
            )
        else:
            result = get_proxy(elt=toproxify, bases=self.interfaces)

        return result

    def check(self, resource):
        """Check input resource related to self interfaces.

        :param Resource resource: resource to check.
        """
        # result equals True by default
        result = True
        # get resource proxy
        proxy = resource.get_proxy()
        # ensure proxy is an iterable
        proxies = proxy if isinstance(proxy, Iterable) else [proxy]
        # check all proxies
        for proxy in proxies:
            # check if resource and proxy respects all interface requirements
            for interface in self.interfaces:
                # if once failed, check is False
                if not interface.check(resource=resource, proxy=proxy):
                    result = False
                    break

        return result

    def get_proxy(self, *args, **kwargs):

        resources = self.resources

        # ensure result is a list of proxies
        result = []
        for name in resources:
            resource = resources[name]
            proxy = resource.get_proxy()
            if isinstance(proxy, Iterable):
                result += proxy
            else:
                result.append(proxy)

        # initialize policy
        policy = self._policy

        # apply policy on the result
        if policy is not None:
            result = policy(port=self, proxies=result)

        return result


class Binding(Component, Resource):
    """Specify how a resource is bound/provided to/by a component.

    In order to be processed, a binding is bound to port(s).
    Related ports are choosen at runtime thanks to start/stop methods.

    Therefore, one binding can be used by several ports.
    """

    CONFIGURATION = 'configuration'

    def __init__(self, configuration=None, *args, **kwargs):
        """
        :param dict configuration: binding configuration.
        """

        super(Binding, self).__init__(*args, **kwargs)

        self.configuration = configuration
