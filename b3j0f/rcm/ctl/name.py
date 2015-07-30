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

from b3j0f.rcm.ctl.core import Controller
from b3j0f.rcm.ctl.annotation import C2CtrlAnnotation, CtrlAnnotation


class NameController(Controller):
    """Controller dedicated to manage components names.
    """

    NAME = '_name'  #: components by name attribute name

    class NameControllerError(Exception):
        """Raised in case of two brother components use the same controller
        name.
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

        return self._get_name()

    def _get_name(self):
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

        self._set_name(value)

    def _set_name(self, name):
        """Change name of components in checking than no other brother
        components has the same controller name.

        :param str name: new name of components.
        """

        # do something only if name is not input name
        if name != self.name:
            # check among components if another component has not the same name
            for component in self._rports:
                # check among _bound_on components
                for rport in component._rports:
                    # check among all ports of _bound_on components
                    for port_name in rport:
                        port = rport[port_name]
                        # compare with controller name
                        component_name = NameController.GET_NAME(port)
                        # if a matching is checked
                        if component_name == name:
                            # raise an exception
                            raise NameController.NameControllerError(
                                'Name {0} already used by {0} in {2}.'.format(
                                    name, port, rport
                                )
                            )

            # if no exception has been raised, update the name
            self._name = name

    def _on_bind(self, component, *args, **kwargs):

        # check if component has no:
        # - brother component with the same name
        # - same controller
        self_name = self.name
        for rport in component._rports:
            try:
                port = NameController.GET_SUB_PORT(rport, self_name)
            except NameController.NameControllerError:
                pass
            else:
                if port is not component:
                    raise NameController.NameControllerError(
                        'Component name {0} is already used by {1} in {2}'
                        .format(
                            self_name, port, rport
                        )
                    )
        else:
            super(NameController, self)._on_bind(
                component=component, *args, **kwargs
            )

    @staticmethod
    def GET_NAME(component):
        """Get name of component.

        :return: component controller name.
        :rtype: str
        """

        return NameController._GET(
            _component=component, _attr='name'
        )

    @staticmethod
    def SET_NAME(component, name):
        """Change name of component.

        :param Component component: component where change controller name.
        :param str name: new name of components.
        """

        NameController._SET(
            _component=component, _attr='name', _value=name
        )

    @staticmethod
    def GET_PORTS_BY_NAME(component, *names):
        """Get ports by NameController.name.

        :param Component component: component from where find ports.
        :param list names: port name(s) to find.
        """

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
        result = "{0}-{1}".format(name, component.uid)
        return result

    @staticmethod
    def GET_SUB_COMPONENT(component, *names):
        """Do a depth search among all sub-ports where controller name matches
        with input names in the same order of depthering.

        :param Component component: component to parse with controller names.
        :param list names: list of controller names to search on.
        :return: sub-port which is designated by list of input names hierarchy.
            None if hierarchy does not match with input names.
        :raises: NameController.NameControllerError if names do not match with
            sub-ports.
        """

        result = None
        # start from the input component
        port = component
        # iterate on all input names
        for name in names:
            # get port by controller name
            ports = NameController.GET_PORTS_BY_NAME(port, name)
            # if ports is not empty
            if ports:
                # update port with first encountered port
                for name in ports:
                    port = ports[name]
            else:  # otherwise, raise a NameControllerError
                raise NameController.NameControllerError(
                    'No component ports of {0} exist with name {1}'.format(
                        port, name
                    )
                )
        else:  # if all names have been searched, result is port
            result = port

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
