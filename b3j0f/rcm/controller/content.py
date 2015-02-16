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

__all__ = ['ContentController', 'Content', 'Add', 'Remove']

from b3j0f.rcm.core import Component
from b3j0f.rcm.controller.core import Controller
import b3j0f.rcm.controller.name
from b3j0f.rcm.controller.impl import Context, ParameterizedImplAnnotation


class ContentController(Controller):
    """In charge of inner composition between components.
    """

    class ContentError(Exception):
        pass

    CONTENT = '_content'

    __slots__ = (CONTENT, ) + Controller.__slots__

    def __init__(self, content=None, *args, **kwargs):
        """
        :param content: inner components.
        :type content: Component or list
        """

        super(ContentController, self).__init__(*args, **kwargs)

        self.content = content

    @property
    def content(self):
        return [self._content]

    @content.setter
    def content(self, value):

        self._content = set()

        if isinstance(value, Component):
            value = [value]

        for component in value:
            self += component

    def __iadd__(self, value):

        if isinstance(value, Component):
            value = [value]

        names = set(
            b3j0f.rcm.controller.name.NameController.get_name(component)
            for component in self._content
        )

        for component in value:
            cname = b3j0f.rcm.controller.name.NameController.get_name(component)
            if cname is not None and cname not in names:
                self._content.add(component)
            else:
                raise ContentController.ContentError(
                    "Impossible to add component {0}. Name {1} already used."
                    .format(component, cname)
                )
            Add.apply(component=component)

    def __isub__(self, value):

        if isinstance(value, Component):
            value = set([value])
        else:
            value = set(value)

        self._content -= value

        for component in value:
            Remove.apply(component=component)

    @staticmethod
    def get_content(component):
        """Get input component content.

        :param component: component from where get content.
        :return: list of components or None if no ContentController.
        """

        result = None

        cc = ContentController.get_controller(component=component)
        if cc is not None:
            result = cc.content

        return result

    @staticmethod
    def add(component, content):
        """Add content to input component.

        :param Component component: component from which add content.
        :param content: components to add.
        :type content: Component or iterable of Components
        """

        cc = ContentController.get_controller(component=component)
        if cc is not None:
            cc += content

    @staticmethod
    def remove(component, content):
        """Remove content from input component.

        :param Component component: component from which remove content.
        :param content: components to remove.
        :type content: Component or iterable of Components
        """

        cc = ContentController.get_controller(component=component)
        if cc is not None:
            cc -= content


class Content(Context):
    """Inject ContentController in an implementation.
    """

    __slots__ = Context.__slots__

    def __init__(self, name=ContentController.ctrl_name(), *args, **kwargs):

        super(Content, self).__init__(name=name, *args, **kwargs)


class Add(ParameterizedImplAnnotation):
    """Fired when related component is added to a new parent component.
    """

    pass


class Remove(ParameterizedImplAnnotation):
    """Fired when related component is removed from a parent component.
    """

    pass
