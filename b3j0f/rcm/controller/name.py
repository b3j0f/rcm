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

__all__ = ['NameController', 'Name', 'SetName', 'GetName']

from b3j0f.rcm.controller.core import Controller
from b3j0f.rcm.controller.annotation import C2CtrlAnnotation, CtrlAnnotation


class NameController(Controller):
    """Controller dedicated to manage component name.
    """

    NAME = '_name'  #: name attribute field name

    #: content controller field name
    CONTENT_CONTROLLER = '_content_controller'

    class NameControllerError(Exception):
        """
        Raised for error in processing a NameController.
        """

        pass

    def __init__(self, name=None, *args, **kwargs):
        """
        :param str name: component name.
        """

        super(NameController, self).__init__(*args, **kwargs)

        self._name = name
        from b3j0f.rcm.controller.content import ContentController
        self._content_controller = ContentController

    @property
    def name(self):
        """Get component name.
        """

        return self._name

    @name.setter
    def name(self, value):
        """Change of component name only if there are not other components at
        the same level which have the same name.
        """

        if self._name != value:
            for component in self.components:
                ctrl = self._content_controller.get_controller(
                    component=component
                )
                if ctrl is not None:
                    pcomponents = ctrl.parent_components
                    for pcomponent in pcomponents:
                        pctrl = self._content_controller.get_controller(
                            component=pcomponent
                        )
                        ccomponents = pctrl.children_components
                        for ccomponent in ccomponents:
                            if ccomponent is not self:
                                nctrl = NameController.get_controller(
                                    component=ccomponent
                                )
                                if nctrl is not None and nctrl.name == value:
                                    raise NameController.NameControllerError(
                                        "Impossible to rename {0} by {1}. {2}"
                                        .format(
                                            component,
                                            value,
                                            "{0} has the same name".format(
                                                ccomponent
                                            )
                                        )
                                    )

    @staticmethod
    def get_name(component):
        """Get component name.
        """

        result = None

        name_controller = NameController.get_controller(component)

        if name_controller is not None:
            result = name_controller.name

        return result

    @staticmethod
    def set_name(component, name):
        """
        Change component name.
        """

        name_controller = NameController.get_controller(component)

        if name_controller is not None:
            name_controller.name = name


class Name(C2CtrlAnnotation):
    """Inject Name controller in an implementation.
    """

    def get_value(self, component, *args, **kwargs):

        return NameController.get_controller(component)


class SetName(CtrlAnnotation):
    """Bind setter implementation methods to the name controller.
    """

    __slots__ = CtrlAnnotation.__slots__

    def get_resource(self, component, *args, **kwargs):

        result = None

        nc = NameController.get_controller(component=component)

        if nc is not None:
            result = nc.name

        return result


class GetName(CtrlAnnotation):
    """Bind getter implementation methods to the name controller.
    """

    __slots__ = CtrlAnnotation.__slots__

    def apply_on(self, component, attr, *args, **kwargs):

        name = attr()

        nc = NameController.get_controller(component=component)

        if nc is not None:
            nc.name = name
