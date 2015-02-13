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

__all__ = ['Controller', 'ImplAnnotation', 'Controllers']

from b3j0f.utils.path import getpath
from b3j0f.annotation import Annotation
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
        :param components:
        """

        super(Controller, self).__init__(*args, **kwargs)
        # set components
        self.components = set() if components is None else components
        # set impl annotation types
        self.impl_ann_types = set() if impl_ann_types is None else set(
            impl_ann_types
        )

    @property
    def components(self):
        """Get a copy of components.
        """
        return set(self._components)

    @components.setter
    def components(self, value):
        """Change set of components.

        :param value: new components to use.
        :type value: Component or iterable of Components
        """
        # ensure value is a set of components
        if isinstance(value, Component):
            value = set([value])
        else:
            value = set(value)
        # unbind from old components
        old_components = self.components - value
        for component in old_components:
            del component[self.get_name()]
        # update new components
        self._components = value

    @classmethod
    def get_name(cls):
        """Get controller unique name.

        :return: cls python path.
        :rtype: str
        """

        return getpath(cls)

    def bind(self, component, name, *args, **kwargs):
        # add component to self.components
        self.components.add(component)
        # apply impl_ann_types
        for annotation in self.impl_ann_types:
            annotation.apply(component=component)

    def unbind(self, component, name, *args, **kwargs):
        # remove component from self.components
        self.components.remove(component)
        # unapply impl_ann_types
        for annotation in self.impl_ann_types:
            annotation.unapply(component=component)

    @classmethod
    def get_controller(cls, component):
        """Get controller from input component.

        :param component: component from where get cls controller.
        :return: controller or None if controller does not exist.
        :rtype: Controller
        """

        result = component.get(cls.get_name())

        return result


class ImplAnnotation(Annotation):
    """Annotation dedicated to Impl implementations.
    """

    def apply_on(self, component, impl, attr=None):
        """Callback when Impl component renew its implementation.

        :param Component component: business implementation component.
        :param impl: component business implementation.
        :param attr: business implementation attribute.
        """

        pass

    def unapply_on(self, component, impl, attr=None):
        """Callback when Impl component change of implementation.

        :param Component component: business implementation component.
        :param impl: component business implementation.
        :param attr: business implementation attribute.
        """

        pass

    @classmethod
    def _process(cls, component, impl, check=None, _apply=True):
        """Apply all cls annotations on component and impl.

        :param Component component: business implementation component.
        :param impl: component business implementation.
        :param check: check function which takes in parameter an annotation in
        order to do annotation.apply_on. If None, annotations are applied.
        """

        annotations = cls.get_annotations(impl)
        for annotation in annotations:
            if check is None or check(annotation):
                if _apply:
                    annotation.apply_on(component=component, impl=impl)
                else:
                    annotation.unapply_on(component=component, impl=impl)

        for field in dir(impl):
            attr = getattr(impl, field)
            annotations = cls.get_annotations(field, ctx=impl)
            for annotation in annotations:
                if check is None or check(annotation):
                    if _apply:
                        annotation.apply_on(
                            component=component, impl=impl, attr=attr
                        )
                    else:
                        annotation.unapply_on(
                            component=component, impl=impl, attr=attr
                        )

    @classmethod
    def apply(cls, component, impl, check=None):
        """Apply all cls annotations on component and impl.

        :param Component component: business implementation component.
        :param impl: component business implementation.
        :param check: check function which takes in parameter an annotation in
        order to do annotation.apply_on. If None, annotations are applied.
        """

        return cls._process(
            component=component, impl=impl, check=check, _apply=True
        )

    @classmethod
    def unapply(cls, component, impl, check=None):
        """Unapply all cls annotations on component and impl.

        :param Component component: business implementation component.
        :param impl: component business implementation.
        :param check: check function which takes in parameter an annotation in
        order to do annotation.apply_on. If None, annotations are applied.
        """

        return cls._process(
            component=component, impl=impl, check=check, _apply=False
        )


class Controllers(ImplAnnotation):
    """Component implementatoin annotation in charge of specifying component
    controllers.
    """

    CONTROLLERS = 'controllers'

    __slots__ = (CONTROLLERS, ) + ImplAnnotation.__slots__

    def __init__(self, controllers, *args, **kwargs):
        """
        :param controllers: controllers to bind to component.
        :type controllers: Controller, Controller class or list of previous
        objects.
        """
        super(Controllers, self).__init__(*args, **kwargs)

        self.controllers = controllers

    def apply_on(self, component, *args, **kwargs):

        # iterate on all self controllers
        for controller in self.controllers:
            # if controller is a Controller class, then instantiate it
            if issubclass(controller, Controller):
                controller = controller()
            # if controller is an instance of Controller
            if isinstance(controller, Controller):
                # bind it with its name
                component[controller.get_name()] = controller

    def unapply_on(self, component, *args, **kwargs):

        # iterate on all self controllers
        for controller in self.controllers:
            # unbind it with its name
            del component[controller.get_name()]
