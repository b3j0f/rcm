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

from b3j0f.utils.version import basestring
from b3j0f.rcm.ctrl.core import Controller
from b3j0f.rcm.ctrl.annotation import C2CtrlAnnotation, CtrlAnnotation


class NameController(Controller):
    """Controller dedicated to manage components names.
    """

    NAME = '_name'  #: components by name attribute name

    class NameControllerError(Exception):
        """
        Raised for error in processing a NameController.
        """
        pass

    def __init__(self, name=None, *args, **kwargs):
        """
        :param str name: name of components.
        """

        super(NameController, self).__init__(*args, **kwargs)

        self._name = name

    @property
    def name(self):
        """Get name of components.

        :return: name of components.
        :rtype: str
        """

        return self.get_name()

    def get_name(self):
        """Get name of components.

        :return: component name.
        :rtype: str
        """

        return self._name

    @name.setter
    def name(self, value):
        """Change name of components.

        :param str value: new name of components.
        """

        self.set_name(value)

    def set_name(self, name):
        """Change name of components in checking than no other brother
        components has the same controller name.

        :param str name: new name of components.
        """
        # do something only if name is not input name
        if name != self.name:
            # check among components if another component has not the same name
            for component in self.components:
                # check among _bound_on components
                for bound_on in component._bound_on:
                    # check among all ports of _bound_on components
                    for port_name in bound_on:
                        port = bound_on[port_name]
                        # compare with controller name
                        component_name = NameController.GET_NAME(port)
                        # if a matching is checked
                        if component_name == name:
                            # raise an exception
                            raise NameController.NameControllerError(
                                'Name {0} already used by {0} in {2}.'.format(
                                    name, port, bound_on
                                )
                            )

            # if no exception has been raised, update the name
            self._name = name

    @staticmethod
    def GET_NAME(component):
        """Get name of components.

        :return: component name.
        :rtype: str
        """

        return NameController._PROCESS(
            _component=component, _method='get_name'
        )

    @staticmethod
    def SET_NAME(component, name):
        """Change name of components.

        :param str name: new name of components.
        """

        NameController._SET(
            _component=component, _attr='set_name', _value=name
        )

    @staticmethod
    def GET_PORTS_BY_NAME(component, names):
        """Get ports by NameController.name.

        :param names: port name(s) to find.
        :type names: str or Iterable
        """

        if isinstance(names, basestring):
            names = [names]

        result = component.get_ports(
            select=lambda name, port: NameController.GET_NAME(port) in names
        )

        return result

    @staticmethod
    def GET_UNAME(component):
        """Get unique component name.

        :return: str of form {name}-{component.id}.
        :rtype: str
        """

        name = NameController.GET_NAME(component=component)
        result = "{0}-{1}".format(name, component.id)
        return result

    @staticmethod
    def GET_PORT(component, *names):
        """Do a depth search among all sub-ports where controller name matches
        with input names in the same order of depthering.

        :return: sub-port which is designated by list of input names hierarchy.
        """

        _component = component

        for name in names:
            ports = NameController.GET_PORTS_BY_NAME(
                component=_component, names=name
            )



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
