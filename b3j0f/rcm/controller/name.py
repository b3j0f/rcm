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

"""Module in charge of bind a logical name to components.
"""

__all__ = ['NameController', 'SetNameCtrl', 'SetName', 'GetName']

from collections import Iterable

from b3j0f.utils.version import basestring
from b3j0f.rcm.core import Component
from b3j0f.rcm.controller.core import Controller
from b3j0f.rcm.controller.annotation import C2CtrlAnnotation, CtrlAnnotation


class NameController(Controller):
    """Controller dedicated to manage components names.
    """

    CMPTS_BY_NAME = '_cmpts_by_name'  #: components by name attribute name

    class NameControllerError(Exception):
        """
        Raised for error in processing a NameController.
        """

        pass

    def __init__(self, cmpts_by_name=None, *args, **kwargs):
        """
        :param dict cmpts_by_name: component names by components.
        """

        super(NameController, self).__init__(*args, **kwargs)

        self._cmpts_by_name = cmpts_by_name

    @property
    def name(self):
        """Get first component name.

        :return: first component name.
        :rtype: str
        """

        result = self.simple_process(self.get_names)
        return result

    @name.setter
    def name(self, value):
        """Set first component name.

        :param str value: new name of the first component.
        """

        component = self.component[0]
        cmpts_by_name = {value: component}
        self.set_names(cmpts_by_name=cmpts_by_name)

    def get_names(self, components=None):
        """Get component name(s).

        :param components: component(s) from where get names. Must be bound to
            this controller. If None, get all component names. If Component,
            get related name.
        :type components: Component or Iterable
        :return: components by name or name if components is a Component..
        :rtype: dict or str
        """

        result = self._cmpts_by_name

        if components is None:
            result = self._cmpts_by_name.copy()

        elif isinstance(components, Component):
            result = None
            for name in self._names:
                component = self._cmpts_by_name[name]
                if component is components:
                    result = name
                    break
        elif isinstance(components, Iterable):
            result = {}
            for name in self._cmpts_by_name:
                component = self._cmpts_by_name[name]
                if component in components:
                    result[name] = component
        else:
            raise TypeError(
                "Wrong components type {0}".format(type(components))
            )

        return result

    def set_names(self, cmpts_by_name):
        """Change of component name(s) only if there are not other components
        at the same level which have the same name.

        :param dict cmpts_by_name: set of components by name.
        :raise: NameControllerError if two components have the same name.
        """

        for name in cmpts_by_name:
            component = cmpts_by_name[name]
            if component in self._bound_to:
                if name in self._cmpts_by_name:
                    named_component = self._cmpts_by_name[name]
                    if named_component != component:
                        self._cmpts_by_name[name] = component
                    else:
                        raise NameController.NameControllerError(
                            "Name conflict by {0} with {1}"
                            .format(component, named_component)
                        )

        return cmpts_by_name

    @staticmethod
    def GET_NAME(component):
        """Get component name.
        """

        return NameController._PROCESS(
            _component=component, _method='get_name'
        )

    @staticmethod
    def GET_NAMES(components):

        return NameController._PROCESSS(
            _components=components, _method='get_names'
        )

    @staticmethod
    def SET_NAME(component, name):
        """Change component name.
        """

        NameController._SET(
            _component=component, _attr='set_name', _value=name
        )

    @staticmethod
    def SET_NAMES(components, cmpts_by_name):
        """Change component names.
        """

        NameController._PROCESSS(
            _component=components, _method='set_names',
            cmpts_by_name=cmpts_by_name
        )

    @staticmethod
    def GET_PORTS(component, names):
        """Get ports by NameController.name.

        :param names: port name(s) to find.
        :type names: str or Iterable
        """

        if isinstance(names, basestring):
            names = {names}

        result = component.get_ports(
            select=lambda name, port: NameController.GET_NAME(port) in names
        )

        return result

    @staticmethod
    def GET_UNAME(component):
        """Get unique component name.

        :return: concatenation of component name and id.
        :rtype: str
        """

        name = NameController.GET_NAME(component=component)
        result = "{0}-{1}".format(name, component.id)
        return result


class SetNameCtrl(C2CtrlAnnotation):
    """Inject Name controller in an implementation.
    """

    def get_value(self, component, *args, **kwargs):

        return NameController.get_controller(component)


class SetName(CtrlAnnotation):
    """Bind setter implementation methods to the name controller.
    """

    __slots__ = CtrlAnnotation.__slots__

    def get_resource(self, component, *args, **kwargs):

        result = NameController.GET_NAME(component=component)

        return result


class GetName(CtrlAnnotation):
    """Bind getter implementation methods to the name controller.
    """

    __slots__ = CtrlAnnotation.__slots__

    def apply_on(self, component, attr, *args, **kwargs):

        name = attr()

        NameController.SET_NAME(component=component, name=name)
