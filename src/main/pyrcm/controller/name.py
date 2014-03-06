from pyrcm.core import Component
from pyrcm.controller.core import ComponentController


class NameController(ComponentController):
    """
    Controller dedicated to manage component name.
    """

    NAME = 'name-controller'

    class NameControllerError(Exception):
        """
        Raised for error in processing a NameController.
        """

        pass

    def __init__(self, membrane=None, name=None):
        """
        Set component name.
        """

        super(NameController, self).__init__(membrane)

        self._name = name if name is not None else \
            Component.GENERATE_INTERFACE_NAME(membrane)

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

        from pyrcm.controller.scope import ScopeController

        try:
            super_components =\
                ScopeController.GET_SUPER_COMPONENTS(self)
            for component in super_components:
                sub_components = ScopeController.GET_SUB_COMPONENTS(component)
                if self.component in sub_components:
                    for children_component in sub_components:
                        children_name =\
                            NameController.get_name(children_component)
                        if children_name == name:
                            raise NameController.NameControllerError(
                                "Two components have the same name %s." % name)
        except ComponentController.NoSuchControllerError:
            pass

        self._name = name

        for setter in self.setters:
            setter(self._name)

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

from pyrcm.core import ComponentAnnotation


class ComponentName(ComponentAnnotation):
    """
    Binds getter and setter implementation methods to the name controller.
    """

    __PVALUE__ = 'pname'

    __PARAM_NAMES_WITH_INDEX__ = {
        __PVALUE__: 0
    }

    def __init__(self, name=None, pname=None):

        self.name = name
        self.pname = pname

    def apply_on(self, component, old_impl, new_impl):

        controller = NameController.GET_CONTROLLER(component)

        name = controller.get_name() if self.name is None \
            else self.name

        param_values_by_name = {
            ComponentName.__PVALUE__: name
        }

        name = self._call_callee(new_impl, param_values_by_name)

        if name is not None:
            controller.set_name(name)
        else:
            controller.setters.add(new_impl)
