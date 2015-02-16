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

__all__ = [
    'PropertyController',  # property controller
    'Property', 'GetProperty', 'SetProperty',  # property annotations
]

from b3j0f.rcm.controller.core import Controller
import b3j0f.rcm.controller.impl


class PropertyController(Controller):
    """Dedicated to manage component parameters.
    """

    PROPERTIES = 'properties'  #: properties field name

    __slots__ = (PROPERTIES, ) + Controller.__slots__

    def __init__(self, properties=None, *args, **kwargs):

        super(PropertyController, self).__init__(*args, **kwargs)
        self.properties = {} if properties is None else properties


class Property(b3j0f.rcm.controller.impl.Context):
    """Inject a PropertyController in an implementation.
    """

    __slots__ = impl.Context.__slots__

    def __init__(
        self, name=PropertyController.ctrl_name(), *args, **kwargs
    ):

        super(Property, self).__init__(name=name, *args, **kwargs)


class _PropertyAnnotation(impl.ParameterizedImplAnnotation):

    NAME = 'name'  #: name field name

    __slots__ = (NAME, ) + impl.ParameterizedImplAnnotation.__slots__

    def __init__(self, name, *args, **kwargs):

        super(_PropertyAnnotation, self).__init__(*args, **kwargs)

        self.name = name


class SetProperty(_PropertyAnnotation):
    """Set a property value from an implementation attr.
    """

    __slots__ = _PropertyAnnotation.__slots__

    def get_resource(self, component, attr, *args, **kwargs):

        pc = PropertyController.get_controller(component=component)

        if pc is not None:
            # get the right name
            name = impl.setter_name(attr) if self.name is None else self.name
            # and the right property
            result = pc.properties[name]

        return result


class GetProperty(_PropertyAnnotation):
    """Get a property value from an implementation attr.
    """

    __slots__ = _PropertyAnnotation.__slots__

    def apply_on(self, component, attr, *args, **kwargs):

        pc = PropertyController.get_controller(component=component)

        if pc is not None:
            # get attr result
            value = attr()
            # get the right name
            name = impl.getter_name(attr) if self.name is None else self.name
            # udate property controller
            pc.properties[name] = value
