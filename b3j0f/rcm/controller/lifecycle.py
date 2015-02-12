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
from b3j0f.rcm.impl import Business


class LifecycleController(ComponentController):
    """
    Dedicated to manage component lifecycle.
    """

    NAME = '/lifecycle-controller'

    START = 'START'
    STOP = 'STOP'

    def __init__(self):
        self._status = LifecycleController.STOP

    def set_status(self, status):
        """
        Change of lifecycle status.
        """

        self._status = status

    def get_status(self):
        """
        Get component lifecycle status.
        """

        return self._status

    def start(self):
        """
        Start all interfaces which are components.
        """

        interfaces = self.get_component().values()

        for interface in interfaces:
            if isinstance(interface, Component) and interface != self:
                interface.start()

        self.set_status(LifecycleController.START)

    def stop(self):
        """
        Stop all interfaces which are components.
        """

        interfaces = self.get_component().values()

        for interface in interfaces:
            if isinstance(interface, Component) and interface != self:
                interface.stop()

        self.set_status(LifecycleController.STOP)

    @staticmethod
    def START(component):
        lifecycle_controller = LifecycleController.GET_CONTROLLER(component)

        if lifecycle_controller is not None:
            lifecycle_controller.start()

    @staticmethod
    def STOP(component):
        lifecycle_controller = LifecycleController.GET_CONTROLLER(component)

        if lifecycle_controller is not None:
            lifecycle_controller.stop()


class Lifecycle(Business.BusinessAnnotation):
    """
    Annotation which permits to link lifecycle status changement with a \
    business method.
    """

    def __init__(self, status):
        self.status = status
