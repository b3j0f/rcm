from pyrcm.core import Component
from pyrcm.controller.core import Controller


class LifecycleController(Controller):
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


from pycoann.core import Decorator


class Lifecycle(Decorator):
    """
    Decorator which permits to link lifecycle status changement with a \
    business method.
    """

    def __init__(self, status):
        self.status = status
