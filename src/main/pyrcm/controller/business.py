from pyrcm.controller.core import Controller
from pyrcm.controller.parameter import ParameterController
from pycoann.core import Decorator, DecoratorWithoutParameters
from pycoann.binding import Interface


class BusinessController(Controller):
    """
    Dedicated to manage comopnent business.
    """

    def renew_implementation(self, implementation_type):
        """
        Instantiate business element and returns it.
        The instantiation is done with parameters and references of this \
component.
        """

        # parameters to call in implementation_type
        parameters = dict()

        # fill parameters with component parameters
        try:
            parameterController = \
                ParameterController.GET_CONTROLLER(self)
            for name in parameterController.get_parameter_names():
                parameter = parameterController.get_parameter(name)
                parameters[name] = parameter
        except Controller.NoSuchControllerError:
            pass

        # fill parameters with component client interfaces
        for interface_name in self.component.get_interfaces():
            interface = self.component.get_interface(interface_name)
            if isinstance(interface, Interface) and not interface.is_server():
                parameters[interface_name] = interface

        result = implementation_type(**parameters)

        self.set_implementation(result)

        return result

    def get_implementation(self):
        """
        Get component implementation.
        """

        return self.implementation

    def set_implementation(self, implementation):
        """
        Set component implementation.
        """

        self.implementation = implementation

        fields_with_decorators = Context.get_decorated_fields(implementation)
        for field_with_decorators in fields_with_decorators:
            field = field_with_decorators[0]
            field(implementation, self.get_component())

from pycoann.decorator import MaxCount
from pyrcm.core import Component


@MaxCount()
class ComponentBusiness(Decorator):
    """
    Dedicated to decorate a class in order to generate a component with at \
least a BusinessController and additional controllers and named services.
    """

    REGISTERED_BUSINESS_COMPONENTS = ()

    def __init__(
        self, controller_types=(), *service_types, **named_service_types
    ):
        """
        Initialize this decorator with controller types and services.
        """
        self.super(ComponentBusiness).__init__()

        # add business controller by default
        controller_types.add(BusinessController)
        self.controller_types = controller_types
        self.service_types = service_types
        self.named_service_types = named_service_types

    @staticmethod
    def new_component(business_type):

        result = None

        component_business = ComponentBusiness.get_decorator(business_type)
        if component_business is not None:
            result = Component()
            for controller_type in component_business.controller_types:
                controller_type(component_business)
            for service_type in component_business.service_types:
                Interface(result, interface_type=service_type)
            for service_name, service_type in\
                    component_business.named_service_types.iteritems():
                Interface(
                    result, name=service_name, interface_type=service_type)

            if not component_business.service_types and \
                    not component_business.named_service_types:
                Interface(result, interface_type=business_type)

        return result

from pyrcm.controller.binding import BindingController
from pyrcm.controller.name import NameController
from pyrcm.controller.intent import IntentController
from pyrcm.controller.lifecycle import LifecycleController
from pyrcm.controller.scope import ScopeController


class BasicComponentBusiness(ComponentBusiness):

    def __init__(
        self, controller_types=(), *service_types, **named_service_types
    ):
        controller_types.add(BindingController)
        controller_types.add(NameController)
        controller_types.add(IntentController)
        controller_types.add(LifecycleController)
        controller_types.add(ParameterController)
        controller_types.add(ScopeController)
        self.super(BasicComponentBusiness).__init__(
            controller_types, service_types, named_service_types)


from pyrcm.controller.remote import RemoteController


class RemoteComponentBusiness(BasicComponentBusiness):

    def __init__(
        self, controller_types=(), service_types=None, named_service_types=None
    ):
        controller_types.add(RemoteController)
        self.super(RemoteComponentBusiness).__init__(
            controller_types, service_types, named_service_types)


@MaxCount()
class Context(DecoratorWithoutParameters):
    """
    Used to inject a context component in a component implementation.
    """

    pass
