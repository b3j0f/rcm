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


@BaseComponent(RemoteController)
class RemoveComponent(Component):

    pass
