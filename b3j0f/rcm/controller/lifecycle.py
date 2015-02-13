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
from b3j0f.rcm.controller.impl import (
    Impl, ParameterizedImplAnnotation, Context
)


class LifecycleController(Controller):
    """Dedicated to manage component lifecycle with custom lifecycle.

    Default START and STOP status are defined.
    """

    START = 'START'
    STOP = 'STOP'

    STATUS = '_status'  #: status field name

    __slots__ = (STATUS, ) + Controller.__slots__

    def __init__(self, *args, **kwargs):

        self._status = LifecycleController.STOP

    @property
    def status(self):
        """Get component lifecycle status.
        """

        return self._status

    @status.setter
    def status(self, value):
        """Change of lifecycle status.

        :param str value: new status.
        """

        # do something only if value != self.status
        if value != self._status:
            # array of (impl, component)
            impl_with_components = []
            for component in self.components:
                # get impl
                try:
                    implCtrl = Impl.get_controller(component=component)
                except KeyError:
                    pass
                else:
                    impl = implCtrl.impl
                    # save impl with components in order to apply Before/After
                    impl_with_components.append((impl, component))
            # if impl_with_components is not empty, create the check lambda fn
            if impl_with_components:
                check = lambda ann: ann.status in [None, value]
            # apply before annotations
            for impl, component in impl_with_components:
                Before.apply(
                    component=component,
                    impl=impl,
                    check=check
                )
            # change value
            self._status = value
            # apply after annotations
            for impl, component in impl_with_components:
                After.apply(
                    component=component,
                    impl=impl,
                    check=check
                )

    def start(self):
        """Start all interfaces which are components.
        """

        self.status = LifecycleController.START

    def stop(self):
        """Stop all interfaces which are components.
        """

        self.status = LifecycleController.STOP

    @staticmethod
    def set_status(component, value):

        controller = LifecycleController.get_controller(component)

        if controller is not None:
            controller.status = value

    @staticmethod
    def set_start(component):
        """Start all component lifecycle controllers.
        """

        LifecycleController.SET_STATUS(LifecycleController.START)

    @staticmethod
    def set_stop(component):
        """Stop all component lifecycle controllers.
        """

        LifecycleController.SET_STATUS(LifecycleController.STOP)


class Lifecycle(Context):
    """Inject lifecycle controller in an implementation.
    """

    __slots__ = Context.__slots__

    def __init__(self, name=LifecycleController.get_name(), *args, **kwargs):

        super(Lifecycle, self).__init__(name=name, *args, **kwargs)


class LifecycleAnnotation(ParameterizedImplAnnotation):
    """Base annotation for Before/After change of lifecycle status.
    """

    STATUS = 'status'

    __slots__ = (STATUS, ) + ParameterizedImplAnnotation.__slots__

    def __init__(self, status=None, *args, **kwargs):

        super(LifecycleAnnotation, self).__init__(*args, **kwargs)

        self.status = status

    def get_resource(self, component, *args, **kwargs):

        result = self.status

        if result is None:
            lc_ctrl = LifecycleController.get_controller(component=component)
            if lc_ctrl is not None:
                result = lc_ctrl.status

        return result


class Before(LifecycleAnnotation):
    """Fire method before a lifecycle change of status.
    """

    __slots__ = LifecycleAnnotation.__slots__


class After(LifecycleAnnotation):
    """Fire method after a lifecycle change of status.
    """

    __slots__ = LifecycleAnnotation.__slots__
