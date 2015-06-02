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

"""Contains Component definition.

A Component is like a dictionary where keys are port names and values are
ports.

A port is simply an object accessible from a component and its goal is to
enrich the Component behavior, like non-functional properties (lifecycle, etc.)
or functional properties like references to the environment.

The API respects the PEP8 except for class methods which are in upper case
due to a requirement to distinguish heavily those ones from instance ones
(like in the Fractal Framework), when their behavior is really close to
instance methods.

For example, it is simple to get Component ports with the method get_ports.
In a lazier approach, it is possible to use the Component.GET_PORTS class
method which uses the same logic than the instance method but is specific to
ports which inherits from the Component type.
"""

__all__ = ['Component']

from b3j0f.utils.version import basestring

from uuid import uuid4 as uuid

from collections import Iterable

from inspect import isroutine, getmembers

from re import compile as re_compile


class Component(dict):
    """Respect the component design pattenr with ports and an unique id.

    A port is a couple of (id, resource) where the id is unique among
    Component resources, and a resource is an object which enriches Component
    behavior. In such way, Component are dictionaries where ports are values
    and names are keys.

    For example, let a Component ``C`` and an object ``O``. C['O'] = O is
    similar to O is the port of C with id equals named 'o'.

    A Component also contains in memory a dictionary of port names by Component
    which are bound to it. Its name is _rports like reverse ports.

    For example, let A and B two components. If A['B'] = B, then B._rports[A]
    equals ['B'].
    """

    UID = '_uid'  #: uid field name
    RPORTS = '_rports'  #: rports field name

    def __init__(
        self, uid=None, ports=None, namedports=None
    ):
        """Constructor which register ports with generated name and named
        interfaces.

        :param string _uid: component uid. Generated if None.
        :param list ports: list of ports to bind.
        :param dict namedports: set of ports to bind by name.
        """

        super(Component, self).__init__()

        # initialiaze private attributes
        self._rports = {}

        # save _uid
        self._uid = uuid() if uid is None else uid
        # save ports
        if ports is not None:
            for port in ports:
                self.set_port(port=port)
        # save named ports
        if namedports is not None:
            for name in namedports:
                port = namedports[name]
                self.set_port(port=port, name=name)

    def __hash__(self):

        return self.hash()

    def hash(self):
        """Get self hash value.
        """

        return hash(self._uid)

    def __delitem__(self, key):

        self.remove_port(name=key)

    def get_port(self, *names):
        """Get a sub-port where hierarchy order respects the input name order.

        :param list names: port names hierarchy.
        :return: sub-port where port names respect input name order.
        :raises: KeyError if port hierarchy does not correspond with names.
        """
        # default result is None
        result = None
        # use the variable port in order to parse port hierarchy
        port = self
        # iterate on names
        for name in names:
            # udpate port with port[name]
            port = port[name]
        else:  # if all names have been founded, result equals port
            result = port

        return result

    def remove_port(self, name):
        """Remove a port by name and returns it.

        :param str name: port name to remove.
        :return: port.
        :raises: KeyError if name is not a bound port name.
        """

        # if port is a component
        result = self[name]

        if isinstance(result, Component):
            # unbind it from self
            result._on_unbind(component=self, name=name)
        # and call super __delitem__
        super(Component, self).__delitem__(name)

        return result

    def __setitem__(self, key, value):

        self.set_port(name=key, port=value)

    def set_port(self, port, name=None):
        """Set new port with input name. And returns previous port if exists.

        :param port: new port to bind.
        :param str name: port name to bind. If None, generated.
        :return: (name, old port) if name already used, otherwise (name, None).
        :rtype: tuple
        """

        # default old_port
        old_port = None

        # generate name if None
        if name is None:
            # in ensuring the new generated name does not exist in self
            while True:
                name = uuid()
                if name not in self:
                    break

        # unbind old component
        if name in self:
            old_port = self[name]
            if isinstance(old_port, Component):
                old_port._on_unbind(component=self, name=name)
        # if port is a component
        if isinstance(port, Component):
            # bind it to self
            port._on_bind(component=self, name=name)
        # and call super __setitem__
        super(Component, self).__setitem__(name, port)

        result = name, old_port

        return result

    def __str__(self):

        result = '{0}({1})'.format(self.__class__, self.hash())

        return result

    def __repr__(self):

        result = super(Component, self).__repr__()

        result = '{0}({1}'.format(self.__class__, result)

        for name, attr in getmembers(self, lambda m: not isroutine(m)):
            if 'a' <= name[0] <= 'z':  # display only public attributes
                result = '{0}, {1}={2}'.format(result, name, attr)

        result += ')'

        return result

    def __del__(self):

        self.delete()

    def delete(self):
        """Delete this component.
        """

        # remove all ports
        self.clear()

    def clear(self):

        for portname in list(self.keys()):
            del self[portname]

    def __contains__(self, value):
        """Check if value is in self ports depending on value type:

        - str: search among port names then among ports.
        - other: search among ports.

        :param value: value to search among ports or port names.
        :type value: str or object
        :return: True if value is among self ports.
        :rtype: bool
        """

        return self.contains(name_or_port=value)

    def contains(self, name_or_port):
        """Check if name_or_port is in self ports depending on type:

        - str: search among port names then among ports.
        - other: search among ports.

        :param name_or_port: name_or_port to search among ports or port names.
        :type name_or_port: str or object
        :return: True if name_or_port is among self ports.
        :rtype: bool
        """

        result = False

        # in case of str, search among keys
        if isinstance(name_or_port, basestring):
            result = super(Component, self).__contains__(name_or_port)

        if not result:  # otherwise, search among values
            result = name_or_port in self.values()

        return result

    def update(self, values=None, **kwargs):
        # bind manually all ports
        if isinstance(values, dict):
            for name in values:
                value = values[name]
                self[name] = value

        for name in kwargs:
            value = kwargs[name]
            self[name] = value

    def setdefault(self, key, default=None):

        if default is None:
            result = super(Component, self).setdefault(key, default)
        else:
            if key not in self:  # bind manually all ports
                self[key] = default
            result = self[key]

        return result

    def pop(self, key, *default):

        result = default[0] if default else None
        # unbind manually port
        if key in self.keys():
            result = self[key]
            del self[key]
        elif not default:
            raise KeyError("Port {0} does not exist in {1}".format(key, self))

        return result

    def _on_bind(self, component, name):
        """Callback method before self is bound to a component.

        :param Component component: new component from where this one is bound.
        :param str name: port name from where self is bound to component.
        """

        # add reference to rports
        self._rports.setdefault(component, set()).add(name)

    def _on_unbind(self, component, name):
        """Callback method before self is bound to a component.

        :param Component component: component from where this one is unbound.
        :param str name: port name from where self is unbound.
        """

        # remove reference to rports
        rports = self._rports[component]
        rports.remove(name)
        if not rports:
            del self._rports[component]

    @property
    def uid(self):
        """Get self unique id.
        """

        return self._uid

    def get_ports(self, names=None, types=None, select=lambda *p: True):
        """Get ports related to names and types.

        :param names: port (regex) names to search for.
        :type names: str or list
        :param types: port types to search for.
        :type types: type or iterable of types
        :param bool raiseError: raise an error if no port is found.
        :param select: boolean selection function which takes a name and a port
            in parameters. True by default.

        :return: dictionary of ports by name.
        :rtype: dict
        """

        result = {}

        # ensure types is a tuple of classes
        if types is None:
            types = (object, )
        elif isinstance(types, Iterable):
            types = tuple(types)
        # if names exist
        if names is not None:
            # ensure names such as a str
            if isinstance(names, basestring):
                names = [names]
            # for all names
            for name in names:
                # search for exact names
                if name in self:
                    # get port
                    port = self[name]
                    # add port to result if isinstance(port, types)
                    if isinstance(port, types) and select(name, port):
                        result[name] = self[name]
                else:  # search for regex expressions
                    regex = re_compile(name)
                    for portname in self:
                        port = self[portname]
                        if regex.match(portname):
                            if isinstance(port, types) and select(name, port):
                                result[portname] = port
        else:
            # for all ports
            for name in self:
                port = self[name]
                # if isinstance(port, types), add port to result
                if isinstance(port, types) and select(name, port):
                    result[name] = port

        return result

    @classmethod
    def GET_PORTS(cls, component, names=None, select=lambda *p: True):
        """Get all component ports which inherits from this class.

        :param Component component: component from where get ports.
        :param names: port names to get.
        :type names: str or list
        :param select: boolean selection function which takes a name and a port
        in parameters. True by default.
        """

        return component.get_ports(names=names, types=cls, select=select)

    @staticmethod
    def GET_BY_ID(component, uid):
        """Get a component from a component model where uid equals to a
        component uid.

        :param Component component: component.
        :param UUID uid: component uid to find in the component model.
        :return: component where uid is input uid among input component model.
            None if related component does not exist.
        """

        if component.uid == uid:  # check component uid
            result = component
        else:  # parse the component model
            result = None  # default result is None
            visited_uids = set()  # visited uids is a set of uids
            components_to_visit = [component]  # components to visit

            def visit_components(
                components, _components_to_visit=components_to_visit
            ):
                """Try to find a component among input components where uid
                equals parent function uid parameter.

                If not, add components to components_to_visit where uids are
                not in visited_uids.

                :param list components: components to visit.
                :param list _components_to_visit: global components to visit.
                :return: component where uid equals uid, otherwise, None.
                :rtype: Component
                """

                result = None

                # filter components where uids are not in visited_uids
                components = [
                    component for component in components
                    if component.uid not in visited_uids
                ]
                # parse components in case of one uid equals super function uid
                for component in components:
                    component_uid = component.uid
                    if component_uid == uid:
                        result = component
                        break
                    else:
                        visited_uids.add(component_uid)
                else:  # add components in components_to_visit
                    _components_to_visit += components

                return result

            # while there are components to parse
            while components_to_visit and result is None:
                # remove first component to visit
                component = components_to_visit.pop()
                ports = component.values()
                result = visit_components(ports)
                if result is None:
                    rports = component._rports
                    result = visit_components(rports)

        return result
