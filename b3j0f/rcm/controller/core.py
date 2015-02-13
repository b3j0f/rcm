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

__all__ = ['Controller']

from b3j0f.utils.path import getpath
from b3j0f.rcm.core import Component


class Controller(Component):
    """Non-functional component which can be bound to several components.
    """

    class NoSuchControllerError(Exception):
        pass

    COMPONENTS = 'components'  #: components attribute name

    __slots__ = (COMPONENTS, ) + Component.__slots__

    def __init__(self, *args, **kwargs):

        self.components = set()

    @classmethod
    def get_name(cls):
        """Get controller unique name.

        :return: cls python path.
        :rtype: str
        """

        return getpath(cls)

    def bind(self, component, name, *args, **kwargs):
        # add component to self.components
        self.components.add(component)

    def unbind(self, component, name, *args, **kwargs):
        # remove component from self.components
        self.components.remove(component)

    @classmethod
    def get_controller(cls, component):
        """Get controller from input component.

        :param component: component from where get cls controller.
        :return: controller or None if controller does not exist.
        :rtype: Controller
        """

        result = component.get(cls.get_name())

        return result
