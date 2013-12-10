from pyrcm.core import Interface
from pyrcm.controller.core import Controller


class BindingController(Controller):
    """
    Controller dedicated to manage component interface bindings.
    """

    NAME = '/binding-controller'

    def bind(self, interface_name, binding):
        """
        Bind a binding to a component interface_name.
        """

        interface = self.get_component().get(interface_name, None)

        if isinstance(interface, Interface):
            binding = binding(interface)

    def unbind(self, interface_name, binding_name):
        """
        Unbind a binding_name from an interface_name.
        """

        interface = self.get_component().get(interface_name, None)

        if isinstance(interface, Interface):
            del interface[binding_name]

    @staticmethod
    def BIND(component, interface_name, binding):

        binding_controller = component[BindingController.NAME]
        binding_controller.bind(interface_name, binding)

    @staticmethod
    def UNBIND(component, interface_name, binding):

        binding_controller = component[BindingController.NAME]
        return binding_controller.unbind(interface_name, binding)
