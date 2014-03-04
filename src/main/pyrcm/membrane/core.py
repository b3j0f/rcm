from pyrcm.core import Component


class ComponentMembrane(Component):
    """
    Component membrane which manages component controllers.
    """

    NAME = 'membrane'

    """
    Key for business component update implementation method.
    """
    __UPDATE_IMPLEMENTATION__ = 'update_implementation'

    """
    Key for business component update implementation method.
    """
    __UPDATE_IMPLEMENTATION = '_update_implementation'

    def __init__(self, business_component=None, *controllers):

        super(ComponentMembrane, self).__init__()

        if business_component is not None:
            self.set_business_component(business_component)

        self.controllers = tuple()
        self.add_controllers(-1, *controllers)

    def get_business_component(self):

        return self.get_interface(name=Component.NAME, error=False)

    def set_business_component(self, business_component):

        if self.get_business_component() is not business_component:
            self[Component.NAME] = business_component
            business_component.set_interface(
                name=ComponentMembrane.NAME, interface=self)

    def get_controllers(self):
        """
        Get membrane controllers.
        """
        return self.controllers

    def add_controllers(self, index=None, *controllers):
        """
        Add controllers at the given index position (at the end by default).
        """

        if not isinstance(index, int):
            controllers = (index,) + controllers

        controllers = list(controllers)

        if index is None:
            index = len(self.controllers)

        while controllers:
            controller = controllers.pop()
            added = self.add_controller(controller=controller, index=index)
            if added:
                index += 1

    def add_controller(self, controller, index=None):
        """
        Try to add a controller at the given index position
        (at the end by default) if not already present in self controllers.
        Returns True if the controller has been added.
        """

        result = False

        if controller not in self.controllers:
            self_controllers = list(self.controllers)
            if index is None:
                self_controllers.append(controller)
            else:
                self_controllers.insert(index, controller)
            result = True

            self.set_interface(interface=controller)

        return result

    def __iadd__(self, controller):
        if isinstance(controller, list) or \
                isinstance(controller, tuple) or \
                isinstance(controller, set):
            controllers = tuple(controller)
            self.add_controllers(None, *controllers)
        else:
            self.add_controller(controller)
        return self

    def remove_controller(self, controller_name):
        """
        Remove the controller designated by the name.
        """

        self.controllers = tuple(
            [controller for controller in self.controllers
                if controller.NAME != controller_name])

        del self[controller_name]

    def __isub__(self, controller):
        self.remove_controller(controller)
        return self

    def on_set_interface(self, name, old, new):
        """
        Listen update implementation from business component.
        """

        if name == Component.NAME:
            self.on_remove_interface(name, old)

            if new is not None:
                business_component_update_implementation = \
                    getattr(new, ComponentMembrane.__UPDATE_IMPLEMENTATION__)

                setattr(
                    self, ComponentMembrane.__UPDATE_IMPLEMENTATION,
                    business_component_update_implementation)

                def update_business_implementation(old, _new):
                    business_component_update_implementation(old, _new)
                    self.update_business_implementation(old, _new)

                setattr(
                    new, ComponentMembrane.__UPDATE_IMPLEMENTATION__,
                    update_business_implementation)

    def on_remove_interface(self, name, interface):
        """
        Remove listener on business update implementation.
        """

        if name == Component.NAME and interface is not None:
            business_update_implementation = \
                getattr(self, ComponentMembrane.__UPDATE_IMPLEMENTATION)
            if business_update_implementation is not None:
                setattr(
                    interface, ComponentMembrane.__UPDATE_IMPLEMENTATION__,
                    business_update_implementation)

    def update_business_implementation(self, old, new):
        """
        Called when the business component update its implementation.
        The call is redirected to all controllers in the order of adding.
        """

        for controller in self.controllers:
            controller.update_business_implementation(old, new)

    @staticmethod
    def GET_MEMBRANE(component):

        result = component[ComponentMembrane.NAME]

        return result

from pyrcm.core \
    import ComponentAnnotationWithoutParameters


class Membrane(ComponentAnnotationWithoutParameters):
    """
    Dedicated to annotate an implementation method in order to inject \
    a reference to the business component membrane.
    """

    def apply_on(self, business_component, set_membrane):

        try:
            membrane = business_component.get_interface(ComponentMembrane.NAME)
            set_membrane(membrane)

        except Component.NoSuchInterfaceError:
            pass

from pyrcm.core import ComponentAnnotation


class ComponentBusiness(ComponentAnnotation):
    """
    Dedicated to annotate a class in order to generate a component with at \
least a BusinessController and additional controllers and named services.
    """

    def __init__(
        self, membrane_type=None, controller_types=tuple(),
        *service_types, **named_service_types
    ):
        """
        Initialize this decorator with controller types and services.
        """

        super(ComponentBusiness, self).__init__()

        self.membrane_type = membrane_type
        self.controller_types = controller_types
        self.service_types = service_types
        self.named_service_types = named_service_types

    def apply_on(self, business_component, implementation):

        if self.membrane_type is None:
            membrane = ComponentMembrane(business_component)
        else:
            membrane = self.membrane_type(business_component)

        if self.controller_types:
            for controller_type in self.controller_types:
                controller_type(membrane)

        for service_type in self.service_types:
            service_name = Component.GENERATE_INTERFACE_NAME(
                interface=service_type, generated=True)
            business_component.set_interface(
                name=service_name, interface=service_type)

        for service_name, service in self.named_service_types.iteritems():
            business_component.set_interface(service_name, implementation)
