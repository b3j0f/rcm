from pyrcm.core import Component
from pyrcm.controller.core import Controller
from pyrcm.controller.scope import ScopeController


class NameController(Controller):
    """
    Controller dedicated to manage component name.
    """

    NAME = 'name-controller'

    class NameControllerError(Exception):
        """
        Raised for error in processing a NameController.
        """

        pass

    def __init__(self, component, name=None):
        """
        Set component name.
        """

        super(NameController, self).__init__(component)
        self._name = name if name is not None else \
            Component.GENERATE_INTERFACE_NAME(component)

    def get_name(self):
        """
        Get self component name.
        """

        return self._name

    def set_name(self, name):
        """
        Change self component name with input name only if other components \
        in the same parent have not the same name than the input name.
        """

        if self._name == name:
            return

        try:
            super_components =\
                ScopeController.GET_SUPER_COMPONENTS(self.get_component())
            for component in super_components:
                sub_components = ScopeController.GET_SUB_COMPONENTS(component)
                if self.component in sub_components:
                    for children_component in sub_components:
                        children_name =\
                            NameController.get_name(children_component)
                        if children_name == name:
                            raise NameController.NameControllerError(
                                "Two components have the same name %s." % name)
        except Controller.NoSuchControllerError:
            pass

        self._name = name

    @staticmethod
    def GET_NAME(component):
        """
        Get component name.
        """

        result = None

        name_controller = NameController.GET_CONTROLLER(component)

        result = name_controller.get_name()

        return result

    @staticmethod
    def SET_NAME(component, name):
        """
        Change component name.
        """

        name_controller = NameController.GET_CONTROLLER(component)

        if name_controller is not None:
            result = name_controller.set_name(name)

        return result
