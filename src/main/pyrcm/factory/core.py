from pyrcm.core import Component
from pyrcm.controller.name import NameController


class Factory(Component):

    def new_component(component, context):
        pass


class FactoryManager(dict):

    @Reference(name=Factory.NAME)
    def set_factory(self, factory):
        factory_name = NameController.GET_NAME(factory)
        self[factory_name] = factory

    @Service()
    def get_factory(self, name):
        return self.factories
