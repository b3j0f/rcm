from pyrcm.core import Component


class Controller(Component):
    """
    Non fonctional component.
    """

    class NoSuchControllerError(Exception):
        """
        Raised wieh no type of controller exists.
        """

        def __init__(self, controller_type, component):
            super(Controller.NoSuchControllerError, self).__init__(
                "No such controller {0} in {1}".
                format(controller_type, component)
                )

    def __init__(self, component):
        super(Controller, self).__init__(component=component)
        component.set_interface(self)

    def get_component(self):
        """
        Returns self component.
        """

        return self[Component.NAME]

    @classmethod
    def GET_CONTROLLER(controller_type, component):
        """
        Get the component controller which is the same type of controller_type.
        If controller type is not associated to component, a \
NoSuchControllerError is raised.
        """
        result = None

        if isinstance(component, controller_type):
            result = component
        elif isinstance(component, Controller):
            result = controller_type.GET_CONTROLLER(component.get_component())
        else:
            try:
                result = component.get_interface(
                    interface_type=controller_type)
            except Controller.NoSuchControllerError:
                pass

        if result is None:
            raise Controller.NoSuchControllerError(controller_type, component)

        return result
