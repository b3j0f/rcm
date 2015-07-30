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

try:
    from threading import Lock, Condition
except ImportError:
    from dummy_threading import Lock, Condition

from b3j0f.rcm.ctl.core import Controller
from b3j0f.rcm.ctl.annotation import (
    CtrlAnnotationInterceptor, C2CtrlAnnotation
)
from b3j0f.rcm.io.port import Port
from b3j0f.rcm.ctl.content import ContentController
from b3j0f.aop import weave, unweave


class LifecycleController(Controller):
    """Dedicated to manage component lifecycle with custom lifecycle ensured
    by a not typed status.

    Default START and STOP status are defined.

    Even if it is possible to play with different statuses, the lifecycle
    controller uses a list of idle_statuses (contains STOP by default).
    If such status is encountered, the lifecycle will intercept any ports bound
    to the component implementation and keep in memory calls or drop them in
    raising a LifecycleError.
    If memory is used in order to save calls to the business, it is possible to
    choose the memory stack size and the logical order of keeping (KEEP_LAST,
    KEEP_FIRST).

    When a lifecycle controller is halted, the state can be propagated to all
    sub components in the condition a content controller (see boolean propagate
    attribute).
    """

    class LifecycleError(Exception):
        """Handle LifecycleController errors.
        """
        pass

    class _Call(object):
        """Manage calls to a joinpoint in a multi-threading context.

        If disabled, the joinpoint is not proceed.
        """

        __slots__ = ('joinpoint', 'condition', 'enabled')

        def __init__(self, joinpoint):

            super(LifecycleController._Call, self).__init__()

            self.joinpoint = joinpoint
            self.condition = Condition()
            self.enabled = True

        def disable(self):
            """Disable joinpoint proceeding.
            """

            self.enabled = False
            self.condition.notify()

        def enable(self):
            """Enable joinpoint proceeding.
            """

            self.condition.notify()

        def proceed(self):
            """Proceed this call.

            Wait until LifecycleController leave an idle_status or this is
            disabled.

            :return: joinpoint proceeding result.
            :raises: RuntimeError if this is disabled.
            """
            result = None

            self.condition.wait()

            if self.enabled:
                result = self.joinpoint.proceed()
            else:
                raise RuntimeError(
                    "Interrupted call ({0})!".format(self.joinpoint)
                )

            return result

    KEEP_LAST = 'keep_last'  #: keep_last field name
    MEM_SIZE = '_mem_size'  #: mem_size field name

    START = 'START'  #: START status value
    STOP = 'STOP'  #: STOP status value

    IDLE_STATUSES = '_idle_statuses'  #: idle_status field name

    STATUS = '_status'  #: status field name
    PROPAGATE = 'propagate'  #: propagation of changing of status field name

    DEFAULT_KEEP_LAST = False
    DEFAULT_MEM_SIZE = 50  #: default mem size
    DEFAULT_PROPAGATE = True  #: default propagate value
    DEFAULT_IDLE_STATUSES = set([STOP])  #: default idle statuses

    _LOCK = '_lock'  #: private lock field name
    _CALLSTACK = '_callstack'  #: private callstack field name

    def __init__(
            self,
            status=STOP,
            keep_last=DEFAULT_KEEP_LAST,
            mem_size=DEFAULT_MEM_SIZE,
            idle_statuses=None,
            propagate=DEFAULT_PROPAGATE,
            *args, **kwargs
    ):

        super(LifecycleController, self).__init__(*args, **kwargs)

        # init private attributes
        self._status = None
        self._mem_size = None
        self._idle_statuses = None
        self._lock = Lock()
        self._callstack = []
        # init attributes
        self.status = status
        self.keep_last = keep_last
        self.mem_size = mem_size
        self.idle_statuses = (
            LifecycleController.DEFAULT_IDLE_STATUSES if idle_statuses is None
            else idle_statuses
        )
        self.propagate = propagate

    def intercept(self, joinpoint):
        """Called when a business port is intercepted.

        :raises: MemoryError if call is halted and callstack >= mem_size.
        :raises: LifecycleController.LifecycleError if controller is halted and
        mem_size equals 0.
        :raises: RuntimeError if call is canceled.
        """

        self._lock.acquire()

        result = None

        # if this is halted
        if self._status in self._idle_statuses:
            # if mem_size is 0, raise a RuntimeError
            if self._mem_size == 0:
                raise LifecycleController.LifecycleError(
                    "Component is halted!"
                )
            elif len(self._callstack) >= self._mem_size:
                raise MemoryError(
                    "Too much calls ({0}) to halted component".format(
                        self._mem_size
                    )
                )
            else:  # create a call, add it to the callstack and halt it
                # create a new call
                call = LifecycleController._Call(joinpoint=joinpoint)
                # add it to the call stack
                self._callstack.append(call)
                # clean call stack
                self.clean()
                # execute it
                result = call.proceed()

        else:
            result = joinpoint.proceed()

        self._lock.release()

        return result

    def clear(self):
        """Clear call stack.
        """

        self._lock.acquire(False)
        for call in self._callstack:
            call.disable()
        self._callstack = []
        self._lock.release()

    def clean(self):
        """Clean call stack related to mem_size.
        """

        self._lock.acquire(False)
        if len(self._callstack) >= self._mem_size:
            ncalls_to_disable = len(self._callstack) - self._mem_size
            if self.keep_last:
                calls = self._callstack[:ncalls_to_disable]
                self._callstack = self._callstack[ncalls_to_disable:]
            else:
                calls = self._callstack[ncalls_to_disable:]
                self._callstack = self._callstack[:ncalls_to_disable]
            for call in calls:
                call.disable()
        self._lock.release()

    @property
    def mem_size(self):
        """Get self memory size.

        :return: memory size.
        :rtype: int
        """
        return self._mem_size

    @mem_size.setter
    def mem_size(self, value):
        """Change of memory size.

        :param int value: new memory size.
        """

        self._lock.acquire()
        self._mem_size = value
        self.clean()
        self._lock.release()

    @property
    def idle_statuses(self):
        """Get idle statuses.

        :return: set of idle statuses.
        :rtype: set
        """
        return self._idle_statuses

    @idle_statuses.setter
    def idle_statuses(self, value):
        """Change of idle statuses.

        :param set value: idle statuses to use.
        """
        self._lock.acquire()
        self._idle_statuses = value
        self._lock.release()

    @property
    def idle(self):
        """True iif this is idle.

        :return: True iif this status is an idle statuses.
        :rtype: bool
        """
        return self._status in self._idle_statuses

    @property
    def status(self):
        """Get component lifecycle status.
        """

        return self._status

    @status.setter
    def status(self, status):
        """Change of lifecycle status.

        :param str status: new status.
        """

        self._set_status(status)

    def _set_status(self, status):
        """Change of lifecycle status.

        :param str status: new status.
        """

        self._lock.acquire()

        # do something only if status != self.status
        if status != self._status:

            # change status
            self._status = status

            # if lifecycle controller enters in an idle status
            if self.idle:
                # weave advices
                for component in self._rports:
                    ports = Port.GET_PORTS(
                        component=component, select=lambda n, p: p.isoutput
                    )
                    for port in ports:
                        weave(port, advices=self.intercept)

            else:
                # clean call stack
                self.clear()
                # unweave advices
                for component in self._rports:
                    ports = Port.GET_PORTS(
                        component=component, select=lambda n, p: p.isoutput
                    )
                    for port in ports:
                        unweave(port, advices=self.intercept)

            # propagate new status if necessary
            if self.propagate:
                content = ContentController.get_content(component=component)
                for component in content:
                    LifecycleController.SET_STATUS(
                        component=component,
                        status=status
                    )

        self._lock.release()

    def start(self):
        """Start all interfaces which are components.
        """

        self.status = LifecycleController.START

    def stop(self):
        """Stop all interfaces which are components.
        """

        self.status = LifecycleController.STOP

    @staticmethod
    def SET_STATUS(component, status):
        """Change status of the input component lifecycle.

        :param str status: new status to use.
        """
        LifecycleController._PROCESS(
            _component=component, _method='_set_status', status=status
        )


class Lifecycle(C2CtrlAnnotation):
    """Inject lifecycle controller in an implementation.
    """

    def get_value(self, component, *args, **kwargs):

        return LifecycleController.get_ctl(component=component)


class NewLCStatus(CtrlAnnotationInterceptor):
    """Fire method before a lifecycle change of status.

    Specific parameters are Component.set_port parameters:

    - status: new port name.
    """

    def get_target_ctx(self, component, *args, **kwargs):

        lcc = LifecycleController.get_ctl(component=component)

        return lcc._set_status, lcc
