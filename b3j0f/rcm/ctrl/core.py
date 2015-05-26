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
from b3j0f.rcm.ctrl.annotation import CtrlAnnotation


class Controller(Component):
    """Non-functional component which enriches component non-functional
    behaviour in beeing bound to them.
    """

    def delete(self, *args, **kwargs):

        super(Controller, self).delete(*args, **kwargs)
        # unbind from self components
        for component in self._rports.keys():
            Controller.unbind_all(component, self)

    def _on_bind(self, component, *args, **kwargs):

        super(Controller, self)._on_bind(component=component, *args, **kwargs)

        # notify all controllers
        controllers = Controller.GET_PORTS(component=component)
        for portname in controllers:
            controller = controllers[portname]
            controller._on_bind_ctrl(self, component=component)

        # apply all Controller annotations
        CtrlAnnotation.apply_on(component=component, impl=self)

    def _on_bind_ctrl(self, controller, component):
        """Callback when a component is bound to the component.

        :param Controller controller: newly bound controller.
        :param Component component: component using the controller.
        """

        pass

    def _on_unbind(self, component, *args, **kwargs):

        super(Controller, self)._on_unbind(
            component=component, *args, **kwargs
        )

        # notify all controllers
        controllers = Controller.GET_PORTS(component=component)
        for portname in controllers:
            controller = controllers[portname]
            controller._on_unbind_ctrl(self, component=component)

        # unapply all Controller Annotation
        CtrlAnnotation.unapply_from(
            component=component,
            impl=self
        )

    def _on_unbind_ctrl(self, controller, component):
        """Callback when a component is unbound from the component.

        :param Controller controller: newly bound controller.
        :param Component component: component using the controller.
        """

        pass

    def _unary_process(self, _method, *args, **kwargs):
        """Process a controller method such as the controller is bound to one
        component.

        :param MethodType _method: controller method.
        :param list args: _method args.
        :param dict kwargs: _method kwargs.
        :return: _method(components=self.components[0], *args, **kwargs)
            result.
        """

        component = None
        for component in self._rports:
            break

        result = _method(components=component, *args, **kwargs)

        return result

    @staticmethod
    def bind_all(component, *controllers):
        """Bind all controllers to input component.

        :param Component component: component where bind ipnut controllers.
        :param list controllers: controllers to bind to input component.
        """

        for controller in controllers:
            ctrl_name = controller.ctrl_name()
            component[ctrl_name] = controller

    @staticmethod
    def unbind_all(component, *controllers):
        """Unbind all controllers from input component.

        :param Component component: component where unbind input controllers.
        """

        for controller in controllers:
            ctrl_name = controller.ctrl_name()
            component.pop(ctrl_name, None)

    @classmethod
    def ctrl_name(cls):
        """Get controller unique name.

        :return: cls python path.
        :rtype: str
        """

        cls_name = cls.__name__

        result = "/{0}".format(cls_name)

        return result

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
    def get_ctrl(cls, component):
        """Get controller from input component.

        :param component: component from where get cls controller.
        :return: controller or None if controller does not exist.
        :rtype: Controller
        """

        controller_name = cls.ctrl_name()
        result = component.get(controller_name)

        return result

    @classmethod
    def _PROCESSS(cls, _components, _method, *args, **kwargs):
        """Execute a controller class method bound to components.

        :param _components: Component(s) from where find controllers.
        :type _components: Component or Iterable
        :param str _method: controller method name.
        :param list args: controller method args.
        :param dict kwargs: controller method kwargs.
        :return: method result by controller.
        :rtype: dict
        """
        # initialize result
        result = {}

        # ensure _components is a list of components
        if isinstance(_components, Component):
            _components = [_components]

        # get all cls controllers of _components
        controllers = set()
        for component in _components:
            controller = cls.get_ctrl(component)
            if controller is not None:
                controllers.add(controller)
        # update result
        for controller in controllers:
            partial_result = getattr(controller, _method)(*args, **kwargs)
            result[controller] = partial_result

        return result

    @classmethod
    def _SETS(cls, _components, _attr, _value):
        """Set attribute value to cls controllers which are used by
        _components.

        :param _components: Component(s) which use cls controller.
        :type _components: Component or Iterable
        :param str _attr: attribute name to set.
        :param _value: attribute value to set.
        """
        # ensure _components is a list of components
        if isinstance(_components, Component):
            _components = [_components]

        controllers = set()

        # get all cls controllers of _components
        for component in _components:
            controller = cls.get_ctrl(component)
            if controller is not None:
                controllers.add(controller)

        for controller in controllers:
            setattr(controller, _attr, _value)

    @classmethod
    def _PROCESS(cls, _component, _method, *args, **kwargs):
        """Execute a controller class method bound to a component.

        :param Component _component: Component from where find controller.
        :param str _method: controller method name.
        :param list args: controller method args.
        :param dict kwargs: controller method kwargs.
        :return: controller method result.
        """

        result = None

        process_result = cls._PROCESSS(
            _components=_component, _method=_method, *args, **kwargs
        )

        if process_result:
            for controller in process_result:
                result = process_result[controller]
                break

        return result

    @classmethod
    def _SET(cls, _component, _attr, _value):
        """Set an attribute value to cls controller which is used by
        _component.

        :param Component _components: Component which use cls controller.
        :param str _attr: attribute name to set.
        :param _value: attribute value to set.
        """

        cls._SETS(_components=_component, _attr=_attr, _value=_value)
