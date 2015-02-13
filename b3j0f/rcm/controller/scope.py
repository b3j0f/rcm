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

from b3j0f.rcm.controller.core import Controller
from b3j0f.rcm.controller.name import NameController
from b3j0f.rcm.controller.impl import Context
from b3j0f.rcm.controller.lifecycle import LifecycleController


class ScopeController(Controller):

    PARENTS = '_parents'
    CHILDREN = '_children'

    __slots__ = (PARENTS, CHILDREN) + Controller.__slots__

    def __init__(self, parents=None, children=None, *args, **kwargs):
        """
        :param parents: iterable of components.
        :param children: iterable of components.
        """

        super(ScopeController, self).__init__(*args, **kwargs)

        self._parents = set() if parents is None else set(parents)
        self._children = set() if children is None else set(children)

    @property
    def parents(self):
        return self._parents

    @parents.setter
    def parents(self, value):
        self._parents = value

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, value):
        self._children = value

    def add_sub_component(self, component):
        """
        Add input component from self sub components.
        """

        component_name = NameController.get_name(component)

        for sub_component in self.get_sub_components():
            sub_component_name = NameController.get_name(sub_component)
            if component_name == sub_component_name:
                raise NameController.NameControllerError(
                    'Impossible to add component %s. Component %s already \
                    exists with the same name %s.' %
                    (component, sub_component, component_name))

        self._sub_components.append(component)

    def remove_sub_component(self, component):
        """
        Remove input component from self sub components.
        """

        self._sub_components.remove(component)

    def start(self):
        """
        Starts all sub components.
        """
        sub_components = self.get_sub_components()

        for sub_component in sub_components:
            LifecycleController.START(sub_component)

    def stop(self):
        """
        Stop all sub components.
        """

        sub_components = self.get_sub_components()

        for sub_component in sub_components:
            LifecycleController.STOP(sub_component)

    @staticmethod
    def GET_SUPER_COMPONENTS(component):
        """
        Get super components of the input component.
        """

        scope = ScopeController.GET_CONTROLLER(component)
        return scope.get_super_components()

    @staticmethod
    def GET_SUB_COMPONENTS(component):
        """
        Get sub components of the input component.
        """

        scope = ScopeController.GET_CONTROLLER(component)
        return scope.get_sub_components()

    @staticmethod
    def ADD_SUB_COMPONENT(component, component_to_add):
        """
        Get sub components of the input component.
        """

        scope = ScopeController.GET_CONTROLLER(component)
        return scope.add_sub_component(component_to_add)

    @staticmethod
    def REMOVE_SUB_COMPONENT(component, component_to_remove):
        """
        Remove sub component.
        """

        scope = ScopeController.GET_CONTROLLER(component)
        return scope.remove_sub_component(component_to_remove)


class Scope(Context):
    """Inject Scope controller in an implementation.
    """

    __slots__ = Context.__slots__

    def __init__(self, name=ScopeController.get_name(), *args, **kwargs):

        super(Scope, self).__init__(name=name, *args, **kwargs)
