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

__all__ = ['Resource', 'Interface']

from inspect import isclass

from b3j0f.rcm.nf.core import Controller


class Interface(object):
    """Resource interface which is used to check and to generate proxy
    resource.

    Provides a ``py_class`` which is the python interface corresponding to the
    value.
    """

    class ValueError(Exception):
        """Raised while trying to update value.
        """
        pass

    VALUE = '_value'  #: value attribute name
    PYCLS = '_pycls'  #: python class value attribute name

    def __init__(self, value=None):
        """
        :param str value: value interface. Default is object.
        """

        super(Interface, self).__init__()

        self.value = value

    def __repr__(self):

        result = "Interface(id={0}, value={1}, pycls={2})".format(
            id(self), self.value, self.pycls
        )

        return result

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
        # get _pycls
        if value is None:  # if value is None, use object
            value = object
        elif not isclass(value):  # if not class, use py_class generator
            value = self._get_pycls()

        # check type of value
        if isclass(value):  # update attribute only if value is a class
            self._pycls = value
        else:  # otherwise, raise an error
            raise Interface.ValueError(
                "Wrong interface value {0}".format(value)
            )

    @property
    def pycls(self):
        """Get python interface.

        :return: python interface.
        """

        return self._pycls

    def _get_pycls(self):
        """Protected method to override in order to get py_class from input
        value.

        :return: python value conversion.
        :rtype: type
        """

        raise NotImplementedError()

    def is_sub_itf(self, itf):
        """Check if self is a sub interface of itf.

        :param Interface itf: interface to check.
        :return: True iif self.py_class subclass of itf.py_class.
        :rtype: bool
        """

        return issubclass(self.pycls, itf.pycls)


class Resource(Controller):
    """Resource element which implements the proxy design pattern in order
    to separate resource realization from its usage.

    It uses Interfaces in order to describe itself.
    """

    ITFS = '_itfs'  #: interfaces attribute name

    def __init__(self, itfs=(Interface(),), proxy=None, *args, **kwargs):
        """
        :param Iterable itfs: list of Interface which describe this resource.
        :param proxy: default resource proxy.
        """

        super(Resource, self).__init__(*args, **kwargs)

        self._itfs = itfs
        self._proxy = proxy

    @property
    def itfs(self):

        return self._itfs

    @itfs.setter
    def itfs(self, value):

        self._set_itfs(itfs=value)

    def _set_itfs(self, itfs):
        """Change of itfs.

        :param list itfs: list of interfaces to use.
        """

        self._itfs = itfs

    @property
    def proxy(self):
        """Get resource proxy.

        :return: self proxy.
        """

        # result is private self _get_proxy result
        result = self._get_proxy()

        return result

    def _get_proxy(self):
        """Get resource proxy.

        :return: self proxy.
        """

        return self._proxy
