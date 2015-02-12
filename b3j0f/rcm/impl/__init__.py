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

"""
Contains Business component definition.
"""

from b3j0f.rcm import Component
from b3j0f.annotation import Annotation
from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup

from inspect import isclass


class Business(Component):
    """Business Component which uses a class.
    """

    class BusinessAnnotation(Annotation):
        """Annotation dedicated to Business implementations.
        """

        def apply_on(
            self, component, impl, prev_impl=None, attr=None, prev_attr=None
        ):
            """Callback when Business component renew its implementation.

            :param Component component: business implementation component.
            :param impl: component business implementation.
            :param prev_impl: previous component business implementation.
            :param attr: business implementation attribute.
            :param prev_attr: previous business implementation attribute.
            """

            raise NotImplementedError()

        @classmethod
        def apply(cls, component, impl, prev_impl=None):
            """Apply all cls annotations on component and impl.

            :param Component component: business implementation component.
            :param impl: component business implementation.
            :param prev_impl: previous component business implementation.
            """

            annotations = cls.get_annotations(impl)
            for annotation in annotations:
                annotation.apply_on(
                    component=component, impl=impl, prev_impl=prev_impl
                )

            for field in dir(impl):
                attr = getattr(impl, field)
                prev_attr = getattr(prev_impl, field, None)
                annotations = cls.get_annotations(field, ctx=impl)
                for annotation in annotations:
                    annotation.apply_on(
                        component=component, impl=impl, prev_impl=prev_impl,
                        attr=attr, prev_attr=prev_attr
                    )

    CLS = '_cls'  #: cls field name
    IMPL = '_impl'  #: impl field name

    __slots__ = (CLS, IMPL, ) + Component.__slots__

    def __init__(self, cls=None, *args, **kwargs):
        """
        :param cls: class to use.
        :type cls: str or type
        :param dict named_ports: named ports.
        """

        super(Business, self).__init__(*args, **kwargs)

        self.cls = cls

    def renew_impl(self, component=None, cls=None, params={}):
        """Instantiate business element and returns it.

        :param cls: new cls to use. If None, use self.cls.
        :type cls: type or str
        :param dict params: new impl parameters.
        :return: new impl.
        """
        # save prev impl
        prev_impl = self.impl
        # save cls
        self.cls = cls
        # save impl and result
        result = self.impl = self._cls(**params)
        # apply business annotations on impl
        if isinstance(component, Component):
            Business.BusinessAnnotation.apply(
                component=component, impl=self.impl, prev_impl=prev_impl
            )

        return result

    @property
    def cls(self):
        """Get self cls.
        """

        return self._cls

    @cls.setter
    def cls(self, value):
        """Change of cls.

        :param value: new class to use.
        :type value: str or type.
        :raises: TypeError in case of value is not a class.
        """
        # if value is a str, try to find the right class
        if isinstance(value, basestring):
            value = lookup(value)
        # update value only if value is a class
        if isclass(value):
            self._cls = value
            self._impl = None  # and nonify the impl
        else:  # raise TypeError if value is not a class
            raise TypeError('value {0} must be a class'.format(value))

    @property
    def impl(self):
        return self._impl

    @impl.setter
    def impl(self, value):

        # update cls
        self.cls = value.__class__
        # and impl
        self._impl = value


class Context(Business.BusinessAnnotation):
    """Used to inject a context component in a component implementation.
    """

    PARAM = 'param'  #: param field name

    __slots__ = (PARAM, ) + Business.BusinessAnnotation

    def __init__(self, param=None, *args, **kwargs):

        super(Context, self).__init__(*args, **kwargs)

        self.param = param

    def apply_on(
        self, component, prev_impl, new_impl, attr, prev_attr, *args, **kwargs
    ):
        kwargs = {} if self.param is None else {self.param: component}
        # inject the component in the impl
        new_impl(**kwargs)
