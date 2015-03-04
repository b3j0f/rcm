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


class Controller(Component):
    """Non-functional component which can be (un)bound to several components.

    Such controller uses a set of impl annotations which are used in the
    component implementation.
    """

    class NoSuchControllerError(Exception):
        pass

    COMPONENTS = '_components'  #: components attribute name
    IMPL_ANNOTATIONS = 'impl_ann_types'  #: impl_ann_types attribute name

    __slots__ = (COMPONENTS, IMPL_ANNOTATIONS) + Component.__slots__

    def __init__(self, components=None, impl_ann_types=None, *args, **kwargs):
        """
        :param components: Components to bind this controller.
        :type components: list or Component
        :param impl_ann_types: types of ImplAnnotations to (un)apply when this
            controller is bound to a component.
        :type impl_ann_types: list or b3j0f.rcm.controller.impl.ImplAnnotation.
        """

        super(Controller, self).__init__(*args, **kwargs)
        # set components
        self._components = set()
        self.components = components
        # set impl annotation types
        self.impl_ann_types = set() if impl_ann_types is None else set(
            impl_ann_types
        )

    def __del__(self):

        super(Controller, self).__del__()
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

    def on_bind(self, component, name, *args, **kwargs):
        # add component to self.components
        self._components.add(component)
        # apply impl_ann_types
        for annotation in self.impl_ann_types:
            annotation.apply(component=component)

    def on_unbind(self, component, name, *args, **kwargs):
        # remove component from self.components
        self._components.remove(component)
        # unapply impl_ann_types
        for annotation in self.impl_ann_types:
            annotation.unapply(component=component)

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
            controller = component.pop(cls.ctrl_name())
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
