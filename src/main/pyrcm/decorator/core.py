from pycoann.core import Decorator, DecoratorWithoutParameters
from pyrcm.core import Component
from pyrcm.controller.binding import BindingController
from pyrcm.controller.intent import IntentController
from pyrcm.controller.lifecycle import LifecycleController
from pyrcm.controller.parameter import ParameterController
from pyrcm.controller.name import NameController
from pyrcm.controller.scope import ScopeController
from pyrcm.controller.business import BusinessController


class Configurate(Decorator):

    def __init__(self, *controllers, **interfaces):

        self._super(Configurate).__init__()
        self.controllers = controllers
        self.interfaces = interfaces


@Configurate(
    IntentController,
    LifecycleController,
    ParameterController,
    NameController,
    ScopeController,
    BusinessController,
    BindingController)
class BaseComponent(Component):
    """
    Component with default controllers.
    """

    pass


class Reference(Decorator):
    """
    Binding dedicated to manage References.
    """

    def __init__(self, name=None, interface=None):

        self._super(Reference).__init__()
        self.name = name
        self.interface = interface


class Service(Decorator):
    """
    Binding dedicated to manage Services.
    """

    def __init__(self, name=None, interface=None):

        self._super(Service).__init__()
        self.name = name
        self.interface = interface


class Parameter(Decorator):

    def __init__(self, name=None):

        self._super(Parameter).__init__()
        self.name = name


class Component(DecoratorWithoutParameters):

    pass


class Lifecycle(Decorator):

    def __init__(self, status):
        self.status = status


class Binding(Decorator):

    def __init__(self, binding):
        self.binding = binding


class Intent(DecoratorWithoutParameters):

    pass
