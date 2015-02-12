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

__all__ = ['ComponentController', 'Controller']

from inspect import getmembers

from b3j0f.rcm.core import Component
from b3j0f.rcm.membrane.core import ComponentMembrane
from b3j0f.rcm.impl import Business


class ComponentController(Component):
    """
    Non-fonctional component.
    """

    class NoSuchControllerError(Exception):
        """
        Raised when no type of controller exists.
        """

        def __init__(self, controller_type, component):
            super(ComponentController.NoSuchControllerError, self).__init__(
                "No such controller {0} in {1}".
                format(controller_type, component)
            )

    def __init__(self, membrane=None):

        super(ComponentController, self).__init__()

        if membrane is not None:
            self.set_membrane(membrane)

        self.getters = set()
        self.setters = set()

    def get_membrane(self):
        """
        Returns self membrane.
        """

        return self.get_interface(name=ComponentMembrane.NAME, error=False)

    def set_membrane(self, membrane):

        if self.get_membrane() is not membrane:
            self[ComponentMembrane.NAME] = membrane
            membrane.add_controller(self)

    def update_business_implementation(self, old, new):
        """
        Called by membrane when the business component update
        its implementation.
        """

        members = getmembers(new)

        for name, field in members:
            old_field = getattr(old, name, None)

            if self._is_setter(name, old_field, field):
                self.setters.append(field)
            if self._is_getter(name, old_field, field):
                self.getters.append(field)

    def _is_setter(self, name, old_field, new_field):
        """
        Return true if input field is an implementation control setter.
        """

        return False

    def _is_getter(self, name, old_field, new_field):
        """
        Return true if input field is an implementation control getter.
        """

        return False

    @classmethod
    def GET_CONTROLLER(controller_type, component):
        """
        Get the component controller which is the same type of controller_type.
        If controller type is not associated to component, a
        NoSuchControllerError is raised.
        """
        result = None

        if isinstance(component, controller_type):
            result = component
        elif isinstance(component, ComponentController):
            result = controller_type.GET_CONTROLLER(
                component.get_membrane())
        elif isinstance(component, ComponentMembrane):
            try:
                result = component.get_interface(
                    interface_type=controller_type)
            except Component.NoSuchInterfaceError:
                pass
        else:
            try:
                membrane = ComponentMembrane.GET_MEMBRANE(component)
                result = membrane.get_interface(
                    interface_type=controller_type)
            except Component.NoSuchInterfaceError:
                pass

        if result is None:
            raise ComponentController.NoSuchControllerError(
                controller_type, component)

        return result


class Controller(Business.BusinessAnnotation):
    """
    Dedicated to annotate an implementation method in order to inject \
    a reference to the business component controller.
    """

    __PVALUE__ = 'pvalue'
    __PNAME__ = 'pname'

    __PARAM_NAMES_WITH_INDEX__ = {
        __PVALUE__: 0,
        __PNAME__: 1
    }

    def __init__(self, name=None, type=None, pname=None, pvalue=None):
        self.name = name
        self.type = type
        self.pname = pname
        self.pvalue = pvalue

    def apply_on(
        self, component, old_field, new_field
    ):

        controller = None

        membrane = ComponentMembrane.GET_MEMBRANE(component)

        if self.name is not None:

            controller = membrane[self.name]

        elif self.type is not None:

            controller = self.type.GET_CONTROLLER(membrane)

        param_values_by_name = {
            Controller.__PVALUE__: self.name,
            Controller.__PNAME__: controller
        }

        self._call_callee(new_field, param_values_by_name)
