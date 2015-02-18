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
"""

__all__ = ['Component']

from b3j0f.utils.version import basestring

from uuid import uuid4 as uuid

from collections import Iterable


class Component(dict):
    """Component which contains named ports and an id.
    """

    ID = '_id'  #: id field name

    __slots__ = (ID, )

    def __init__(
        self, _id=None, **named_ports
    ):
        """Constructor which register ports with generated name and named
        interfaces.
        """

        super(Component, self).__init__()

        # save _id
        self._id = uuid() if _id is None else _id
        # save interfaces
        for name in named_ports:
            port = named_ports[name]
            self[name] = port

    def __hash__(self):

        return hash(self._id)

    def __delitem__(self, key):

        # if port is a component
        port = self[key]
        if isinstance(port, Component):
            # unbind it from self
            port.unbind(component=self, name=key)
        # and call super __delitem__
        super(Component, self).__delitem__(key)

    def __setitem__(self, key, value):

        # unbind old component
        if key in self:
            old_value = self[key]
            if isinstance(old_value, Component):
                old_value.unbind(component=self, name=key)
        # if value is a component
        if isinstance(value, Component):
            # bind it to self
            value.bind(component=self, name=key)
        # and call super __setitem__
        super(Component, self).__setitem__(key, value)

    def __repr__(self):

        result = super(Component, self).__repr__()

        result = '{0}({1}'.format(self.__class__, result)

        for slot in self.__slots__:
            attr = getattr(self, slot, None)
            result = '{0}, {1}={2}'.format(result, slot, attr)

        result += ')'

        return result

    def __del__(self):

        self.clear()

    def __contains__(self, value):
        """Check if value is in self ports depending on value type:

        - str: search among port names then among ports.
        - other: search among ports.

        :param value: value to search among ports or port names.
        :type value: str or object
        :return: True if value is among self ports.
        :rtype: bool
        """

        result = False

        # in case of str, search among keys
        if isinstance(value, basestring):
            result = super(Component, self).__contains__(value)

        if not result:  # otherwise, search among values
            result = value in self.values()

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

    def clear(self):
        # unbind manually all ports
        for name in self.keys():
            del self[name]

    def pop(self, key, *default):

        result = default
        # unbind manually port
        if key in self.keys():
            result = self[key]
            del self[key]
        else:
            result = super(Component, self).pop(key, *default)

        return result

    def bind(self, component, name):
        """Callback method before self is bound to a component.

        :param Component component: new component from where this one is bound.
        :param str name: port name from where self is bound to component.
        """

        pass

    def unbind(self, component, name):
        """Callback method before self is bound to a component.

        :param Component component: component from where this one is unbound.
        :param str name: port name from where self is unbound.
        """

        pass

    @property
    def id(self):
        """Get self id.
        """

        return self._id

    def get_ports(self, names=None, types=None, select=lambda *p: True):
        """Get ports related to names and types.

        :param names: port names to search for.
        :type names: str or list
        :param types: port types to search for.
        :type types: type or iterable of types
        :param bool raiseError: raise an error if no port is found.
        :param select: boolean selection function which takes a name and a port
        in parameters. True by default.

        :return: dict of ports by name.
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
                if name in self:
                    # get port
                    port = self[name]
                    # add port to result if isinstance(port, types)
                    if isinstance(port, types) and select(name, port):
                        result[name] = self[name]
        else:
            # for all ports
            for name in self:
                port = self[name]
                # if isinstance(port, types), add port to result
                if isinstance(port, types) and select(name, port):
                    result[name] = port

        return result

    @classmethod
    def get_cls_ports(cls, component, names=None, select=lambda *p: True):
        """Get all component ports which inherits from this class.

        :param Component component: component from where get ports.
        :param names: port names to get.
        :type names: str or list
        :param select: boolean selection function which takes a name and a port
        in parameters. True by default.
        """

        return component.get_ports(names=names, types=cls, select=select)
