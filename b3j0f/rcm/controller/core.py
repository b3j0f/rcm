# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2015 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

__all__ = ['Controller']

from b3j0f.rcm.core import Component
from b3j0f.rcm.controller.annotation import CtrlAnnotation


class Controller(Component):
    """Non-functional component which can be (un)bound to several components.
    """

    class NoSuchControllerError(Exception):
        pass

    COMPONENTS = '_components'  #: components attribute name

    def __init__(self, components=None, *args, **kwargs):
        """
        :param components: Components to bind this controller.
        :type components: list or Component
        """

        super(Controller, self).__init__(*args, **kwargs)
        # set components
        self._components = set()
        self.components = components

    def delete(self, *args, **kwargs):

        super(Controller, self).delete(*args, **kwargs)
        # unbind from self components
        for component in self.components:
            Controller.unbind_all(component, self)

    @property
    def components(self):
        """Get a copy of components.
        """
        return list(self._components)

    @components.setter
    def components(self, value):
        """Change set of components.

        :param value: new components to use.
        :type value: Component or iterable of Components
        """

        # ensure value is a set of components
        if value is None:
            value = set()
        elif isinstance(value, Component):
            value = set([value])
        else:
            value = set(value)
        # unbind from old components
        old_components = self._components - value
        for component in old_components:
            Controller.unbind_all(component, self)
        # bind to new components
        for component in value:
            Controller.bind_all(component, self)
        # update new components
        self._components = value

    @classmethod
    def ctrl_name(cls):
        """Get controller unique name.

        :return: cls python path.
        :rtype: str
        """

        cls_name = cls.__name__

        result = "/{0}".format(cls_name)

        return result

    def on_bind(self, component, *args, **kwargs):

        super(Controller, self).on_bind(component=component, *args, **kwargs)

        # add component to self.components
        self._components.add(component)

        # notify all controllers
        controllers = Controller.get_cls_ports(component=component)
        for port_name in controllers:
            controller = controllers[port_name]
            controller.on_bind_ctrl(self, component=component)

        # apply all Controller annotations
        CtrlAnnotation.apply_on(component=component, impl=self)

    def on_bind_ctrl(self, controller, component):
        """Callback when a component is bound to the component.

        :param Controller controller: newly bound controller.
        :param Component component: component using the controller.
        """

        pass

    def on_unbind(self, component, *args, **kwargs):

        super(Controller, self).on_bind(component=component, *args, **kwargs)

        # remove component to self.components
        self._components.remove(component)

        # notify all controllers
        controllers = Controller.get_cls_ports(component=component)
        for port_name in controllers:
            controller = controllers[port_name]
            controller.on_unbind_ctrl(self, component=component)

        # unapply all Controller Annotation
        CtrlAnnotation.unapply_from(
            component=component,
            impl=self
        )

    def on_unbind_ctrl(self, controller, component):
        """Callback when a component is unbound from the component.

        :param Controller controller: newly bound controller.
        :param Component component: component using the controller.
        """

        pass

    @staticmethod
    def bind_all(component, *controllers):
        """Bind all controllers to input component.

        :param Component component: component where bind ipnut controllers.
        :param list controllers: controllers to bind to input component.
        """

        for controller in controllers:
            component[controller.ctrl_name()] = controller

    @staticmethod
    def unbind_all(component, *controllers):
        """Unbind all controllers from input component.

        :param Component component: component where unbind input controllers.
        """

        for controller in controllers:
            component.pop(controller.ctrl_name(), None)

    @classmethod
    def bind_to(cls, components, *args, **kwargs):
        """Bind a controller of type cls to component(s).

        :param components: component(s) to bind to a controller.
        :type components: list or Component
        :param list args: controller varargs initialization.
        :param dict kwargs: controller kwargs initialization.
        :return: bound controller.
        :rtype: cls
        """

        # instantiate a controller
        controller = cls(*args, **kwargs)
        # ensure components is a list of components
        if isinstance(components, Component):
            components = [components]
        # bind the controller in all components
        for component in components:
            component[controller.ctrl_name()] = controller

        return controller

    @classmethod
    def unbind_from(cls, *components):
        """Unbind a controller of type cls from component(s).

        :param components: component(s) from where unbind controllers of type
            cls.
        :type components: list or Component
        :return: unbound controllers.
        :rtype: list
        """

        result = [None] * len(components)

        # unbind all controllers registered by cls.crtl_name()
        for index, component in enumerate(components):
            controller = component.pop(cls.ctrl_name(), None)
            result[index] = controller

        return result

    @classmethod
    def get_controller(cls, component):
        """Get controller from input component.

        :param component: component from where get cls controller.
        :return: controller or None if controller does not exist.
        :rtype: Controller
        """

        controller_name = cls.ctrl_name()
        result = component.get(controller_name)

        return result
