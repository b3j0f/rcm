from pyrcm.core import Component


class Controller(Component):
    """
    Non fonctional component.
    """

    def __init__(self, component):
        super(Controller, self).__init__(component=component)

    def apply(self, component):

        pass

    def get_component(self):
        """
        Returns self component.
        """

        return self[Component.NAME]

    @classmethod
    def GET_CONTROLLER(controller_type, component):
        """
        Get the component controller which is the same type of controller_type.
        """

        if isinstance(component, controller_type):
            result = component
        else:
            result = component.get(controller_type.NAME, None)

        return result
