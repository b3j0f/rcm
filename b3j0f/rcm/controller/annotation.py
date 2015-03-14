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

"""Regroup all controller annotations and utilities in order to develop your
own annotations.
"""

__all__ = [
    'ImplAnnotation', 'Controllers',  # Controller annotation
    'Impl', 'Context',  # impl controller annotations
    'Property', 'GetProperty', 'SetProperty',  # property controller annotation
    'Binding', 'Input', 'Output',  # binding controller annotations
    'Lifecycle', 'Before', 'After',  # lifecycle controller annotations
    'Name', 'GetName', 'SetName',  # name controller annotations
]

from b3j0f.rcm.controller.core import Controller
from b3j0f.rcm.controller.impl import (
    ImplAnnotation, Impl, Context
)
from b3j0f.rcm.controller.property import (
    Property, GetProperty, SetProperty
)
from b3j0f.rcm.controller.binding import Binding, Input, Output
from b3j0f.rcm.controller.lifecycle import Lifecycle, Before, After
from b3j0f.rcm.controller.name import Name, GetName, SetName


class Controllers(ImplAnnotation):
    """Component implementatoin annotation in charge of specifying component
    controllers.
    """

    CONTROLLERS = 'controllers'

    __slots__ = (CONTROLLERS, ) + ImplAnnotation.__slots__

    def __init__(self, controllers, *args, **kwargs):
        """
        :param controllers: controllers to bind to component.
        :type controllers: Controller, Controller class or list of previous
        objects.
        """
        super(Controllers, self).__init__(*args, **kwargs)

        self.controllers = controllers

    def apply_on(self, component, *args, **kwargs):

        # iterate on all self controllers
        for controller in self.controllers:
            # if controller is a Controller class, then instantiate it
            if issubclass(controller, Controller):
                controller = controller()
            # if controller is an instance of Controller
            if isinstance(controller, Controller):
                # bind it with its name
                component[controller.ctrl_name()] = controller

    def unapply_on(self, component, *args, **kwargs):

        # iterate on all self controllers
        for controller in self.controllers:
            # unbind it with its name
            del component[controller.ctrl_name()]
