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

For example, it is simple to get Component ports with the method getports.
In a lazier approach, it is possible to use the Component.GETPORTS class
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
    """Component which contains named ports and an uid.

    A port is just an object which is bound to the component such as
    a dict value where key is port name.

    For example, let a Component C and an object o. C['o'] = o is similar to
    o is the port of C named 'o'.

    A Component also contains in memory a dictionary of port names by Component
    which are bound to it.

    For example, let A and B two components. If B is both ports b0 and b1,
    B keeps references to both port names b0 and b1 thanks to B._boundon dict
    which contains one key A and both values b0 and b1.
    """

    UID = '_uid'  #: uid field name
    BOUND_ON = '_boundon'  #: bound_on field name

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
        self._boundon = {}

        # save _uid
        self._uid = uuid() if uid is None else uid
        # save ports
        if ports is not None:
            for port in ports:
                self.setport(port=port)
        # save named ports
        if namedports is not None:
            for name in namedports:
                port = namedports[name]
                self.setport(port=port, name=name)

    def __hash__(self):

        return self.hash()

    def hash(self):
        """Get self hash value.
        """

        return hash(self._uid)

    def __delitem__(self, key):

        self.removeport(name=key)

    def removeport(self, name):
        """Remove a port by name and returns it.

        :param str name: port name to remove.
        :return: port.
        :raises: KeyError if name is not a bound port name.
        """

        # if port is a component
        result = self[name]

        if isinstance(result, Component):
            # unbind it from self
            result._onunbind(component=self, name=name)
        # and call super __delitem__
        super(Component, self).__delitem__(name)

        return result

    def __setitem__(self, key, value):

        self.setport(name=key, port=value)

    def setport(self, port, name=None):
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
                old_port._onunbind(component=self, name=name)
        # if port is a component
        if isinstance(port, Component):
            # bind it to self
            port._onbind(component=self, name=name)
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

    def _onbind(self, component, name):
        """Callback method before self is bound to a component.

        :param Component component: new component from where this one is bound.
        :param str name: port name from where self is bound to component.
        """

        # add reference to bound_on
        self._boundon.setdefault(component, set()).add(name)

    def _onunbind(self, component, name):
        """Callback method before self is bound to a component.

        :param Component component: component from where this one is unbound.
        :param str name: port name from where self is unbound.
        """

        # remove reference to bound_on
        bound_on = self._boundon[component]
        bound_on.remove(name)
        if not bound_on:
            del self._boundon[component]

    @property
    def uid(self):
        """Get self unique id.
        """

        return self._uid

    def getports(self, names=None, types=None, select=lambda *p: True):
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
    def GETPORTS(cls, component, names=None, select=lambda *p: True):
        """Get all component ports which inherits from this class.

        :param Component component: component from where get ports.
        :param names: port names to get.
        :type names: str or list
        :param select: boolean selection function which takes a name and a port
        in parameters. True by default.
        """

        return component.getports(names=names, types=cls, select=select)
