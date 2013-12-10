from pyrcm.controller import Controller
from pyrcm.controller.name import NameController
from pyrcm.controller.lifecycle import LifecycleController


class ScopeController(Controller):

    NAME = '/scope-controller'

    def __init__(self, component):

        super(ScopeController, self).__init__(component)
        self._sub_components = []
        self._super_components = []

    def get_sub_components(self):

        return self._sub_components

    def get_super_components(self):

        return self._super_components

    def add_sub_components(self, component):

        component_name = NameController.get_name(component)

        for sub_component in self.get_sub_components():
            sub_component_name = NameController.get_name(sub_component)
            if component_name == sub_component_name:
                raise NameController.NameControllerError(
                    'Impossible to add component %s. Component %s already \
                    exists with the same name %s.' %
                    (component, sub_component, component_name))

        self._sub_components.append(component)

    def start(self):
        """
        Starts all sub components.
        """
        sub_components = self.get_sub_components()

        for sub_component in sub_components:
            LifecycleController.START(sub_component)

    def stop(self):
        """
        Stop all sub components.
        """

        sub_components = self.get_sub_components()

        for sub_component in sub_components:
            LifecycleController.STOP(sub_component)

    @staticmethod
    def GET_SUPER_COMPONENTS(component):
        scope = component[ScopeController.NAME]
        return scope.get_super_components()

    @staticmethod
    def GET_SUB_COMPONENTS(component):
        scope = component[ScopeController.NAME]
        return scope.get_sub_components()
