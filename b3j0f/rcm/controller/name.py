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

from b3j0f.rcm import Component
from b3j0f.rcm.controller import ComponentController


class NameController(ComponentController):
    """
    Controller dedicated to manage component name.
    """

    NAME = 'name-controller'

    class NameControllerError(Exception):
        """
        Raised for error in processing a NameController.
        """

        pass

    def __init__(self, membrane=None, name=None):
        """
        Set component name.
        """

        super(NameController, self).__init__(membrane)

        self._name = name if name is not None else \
            Component.GENERATE_INTERFACE_NAME(membrane)

    def get_name(self):
        """
        Get self component name.
        """

        return self._name

    def set_name(self, name):
        """
        Change self component name with input name only if other components \
        in the same parent have not the same name than the input name.
        """

        if self._name == name:
            return

        from pyrcm.controller.scope import ScopeController

        try:
            super_components =\
                ScopeController.GET_SUPER_COMPONENTS(self)
            for component in super_components:
                sub_components = ScopeController.GET_SUB_COMPONENTS(component)
                if self.component in sub_components:
                    for children_component in sub_components:
                        children_name =\
                            NameController.get_name(children_component)
                        if children_name == name:
                            raise NameController.NameControllerError(
                                "Two components have the same name %s." % name)
        except ComponentController.NoSuchControllerError:
            pass

        self._name = name

        for setter in self.setters:
            setter(self._name)

    @staticmethod
    def GET_NAME(component):
        """
        Get component name.
        """

        result = None

        name_controller = NameController.GET_CONTROLLER(component)

        result = name_controller.get_name()

        return result

    @staticmethod
    def SET_NAME(component, name):
        """
        Change component name.
        """

        name_controller = NameController.GET_CONTROLLER(component)

        if name_controller is not None:
            result = name_controller.set_name(name)

        return result

from pyrcm.core import ComponentAnnotation


class GetComponentName(ComponentAnnotation):
    """
    Binds getter implementation methods to the name controller.
    """
    def apply_on(self, component, old_impl, new_impl):

        controller = NameController.GET_CONTROLLER(component)

        name = new_impl()

        controller.set_name(name)

        controller.getters.add(new_impl)


class SetComponentName(ComponentAnnotation):
    """
    Binds setter implementation methods to the name controller.
    """

    __PVALUE__ = 'pname'

    __PARAM_NAMES_WITH_INDEX__ = {
        __PVALUE__: 0
    }

    def __init__(self, name=None, pname=None):

        self.name = name
        self.pname = pname

    def apply_on(self, component, old_impl, new_impl):

        controller = NameController.GET_CONTROLLER(component)

        name = controller.get_name() if self.name is None \
            else self.name

        param_values_by_name = {
            SetComponentName.__PVALUE__: name
        }

        self._call_callee(new_impl, param_values_by_name)

        controller.setters.add(new_impl)
