from pyrcm.binding.core import Interface
from pyrcm.controller.core import Controller


class BindingController(Controller):
    """
    Dedicated to manage component interface bindings.
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

        binding_controller = BindingController.GET_CONTROLLER(component)
        binding_controller.bind(interface_name, binding)

    @staticmethod
    def UNBIND(component, interface_name, binding):

        binding_controller = BindingController.GET_CONTROLLER(component)
        return binding_controller.unbind(interface_name, binding)

from pycoann.core import Annotation


class Reference(Annotation):
    """
    Decorator dedicated to set a reference into business code.
    """

    def __init__(self, name=None, interface=None):

        self._super(Reference).__init__()
        self.name = name
        self.interface = interface


class Service(Annotation):
    """
    Decorator dedicated to provides a function such as a Service.
    """

    def __init__(self, name=None, interface=None, *bindings):

        self._super(Service).__init__()
        self.name = name
        self.interface = interface
        self.bindings = bindings
