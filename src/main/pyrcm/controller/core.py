from pyrcm.core import Component
from pyrcm.membrane.core import ComponentMembrane
from inspect import getargspec


class ComponentController(Component):
    """
    Non-fonctional component.
    """

    class NoSuchControllerError(Exception):
        """
        Raised when no type of controller exists.
        """

        def __init__(self, controller_type, component):
            super(ComponentController.NoSuchControllerError, self).__init__(
                "No such controller {0} in {1}".
                format(controller_type, component)
                )

    def __init__(self, membrane=None):

        super(ComponentController, self).__init__()

        if membrane is not None:
            self.set_membrane(membrane)

    def get_membrane(self):
        """
        Returns self membrane.
        """

        return self.get_interface(name=ComponentMembrane.NAME, error=False)

    def set_membrane(self, membrane):

        if self.get_membrane() is not membrane:
            self[ComponentMembrane.NAME] = membrane
            membrane.add_controller(self)

    def update_business_implementation(self, old, new):
        """
        Called by membrane when the business component update
        its implementation.
        """

        fields_by_name = vars(new)

        for name, field in fields_by_name.iteritems():
            old_field = getattr(old, name, None)

            if self._is_setter(name, old_field, field):
                self.setters.append(field)
            if self._is_getter(name, old_field, field):
                self.getters.append(field)

    def _is_setter(self, name, old_field, new_field):
        """
        Return true if input field is an implementation control setter.
        """

        return False

    def _is_getter(self, name, old_field, new_field):
        """
        Return true if input field is an implementation control getter.
        """

        return False

    @classmethod
    def GET_CONTROLLER(controller_type, component):
        """
        Get the component controller which is the same type of controller_type.
        If controller type is not associated to component, a
        NoSuchControllerError is raised.
        """
        result = None

        if isinstance(component, controller_type):
            result = component
        elif isinstance(component, ComponentController):
            result = controller_type.GET_CONTROLLER(
                component.get_membrane())
        elif isinstance(component, ComponentMembrane):
            try:
                result = component.get_interface(
                    interface_type=controller_type)
            except Component.NoSuchInterfaceError:
                pass
        else:
            try:
                membrane = ComponentMembrane.GET_MEMBRANE(component)
                result = membrane.get_interface(
                    interface_type=controller_type)
            except Component.NoSuchInterfaceError:
                pass

        if result is None:
            raise ComponentController.NoSuchControllerError(
                controller_type, component)

        return result

from pyrcm.core import ComponentAnnotationWithoutParameters


class Controller(ComponentAnnotationWithoutParameters):
    """
    Dedicated to annotate an implementation method in order to inject \
    a reference to the business component controller.
    """

    __PARAM_NAMES_WITH_INDEX__ = {
        'pvalue': 0,
        'pname': 1
    }

    def __init__(self, name=None, type=None, pname=None, pvalue=None):
        self.name = name
        self.type = type
        self.pname = pname
        self.pvalue = pvalue

    def apply_on(self, component, old_impl, new_impl):

        controller = None

        membrane = ComponentMembrane.GET_MEMBRANE(component)

        if self.name is not None:

            controller = membrane[self.name]

        elif self.type is not None:

            controller = self.type.GET_CONTROLLER(membrane)

        kwargs = dict()

        argspec = getargspec(new_impl)

        self._push_param(self.pname, self.name, argspec, kwargs)
        self._push_param(self.pvalue, controller, argspec, kwargs)

        new_impl(**kwargs)
