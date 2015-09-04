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

"""Contains Impl and Property controller definition.
"""

__all__ = [
    'ImplController',  # impl controller
    'SetImplCtl', 'Stateless',  # impl annotations
    'new_component'
]

from inspect import isclass

from b3j0f.annotation.check import Target, MaxCount
from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup
from b3j0f.rcm.core import Component
from b3j0f.rcm.ctl.core import Controller
from b3j0f.rcm.ctl.annotation import CtlAnnotation, C2CtlAnnotation


class ImplController(Controller):
    """Impl Controller which uses a class in order to instantiate a component
    business implementation.
    """

    STATEFUL = 'stateful'  #: stateful property
    CLS = '_cls'  #: cls field name
    IMPL = '_impl'  #: impl field name

    class ImplError(Exception):
        """Handle impl errors.
        """

    def __init__(self, stateful=True, cls=None, impl=None, *args, **kwargs):
        """
        :param bool stateful: stateful property.
        :param cls: class to use.
        :type cls: str or type
        :param impl: class implementation.
        :param dict named_ports: named ports.
        """

        super(ImplController, self).__init__(*args, **kwargs)

        # init public properties
        self.stateful = stateful
        # init private params
        self._impl = None
        self._cls = None
        # init cls
        self.cls = cls
        self.impl = impl

    def get_resource(self, component=None, args=None, kwargs=None):
        """Get resource.
        """
        result = None

        if self.stateful:
            result = self._impl
        else:
            result = self.instantiate(component=component, kwargs=kwargs)

        return result

    def instantiate(self, component=None, args=None, kwargs=None):
        """Instantiate business element and returns it.

        Instantiation parameters depend on 3 levels of customisation in this
        order (related to a component-driven approach):

        - specific parameters ``args`` and ``kwargs`` given in this method.
        - cls parameters given by ParameterizedImplAnnotation.

        :param Component component: specific parent component.
        :param list args: new impl varargs which are specific to this impl.
        :param dict kwargs: new impl kwargs which are specific to this impl.
        :return: new impl.
        :raises: ImplController.ImplError if self.cls is None or instantiation
            errors occur.
        """

        # default result
        result = None

        if self.cls is None:
            raise ImplController.ImplError(
                "ImplController {0} has no class".format(self)
            )
        # init args
        if args is None:
            args = []
        # init kwargs
        if kwargs is None:
            kwargs = {}
        # try to instantiate the implementation
        try:
            result = C2CtlAnnotation.call_setter(
                component=component, impl=self._cls, args=args, kwargs=kwargs,
                force=True
            )
        except Exception as ex:
            raise ImplController.ImplError(
                "Error ({0}) during impl instantiation of {1}".format(ex, self)
            )
        else:  # update self impl
            try:
                self.impl = result
            except Exception as ex:
                raise ImplController.ImplError(
                    "Error ({0}) while changing of impl of {1}".format(
                        ex, self
                    )
                )

        return result

    @property
    def cls(self):
        """Get self cls.
        """

        return self._cls

    @cls.setter
    def cls(self, value):
        """Change of cls.

        :param value: new class to use.
        :type value: str or type.
        :raises: TypeError in case of value is not a class.
        """

        if value is self._cls:
            pass  # do nothin if cls is value

        elif value is not None:
            # if value is a str, try to find the right class
            if isinstance(value, basestring):
                value = lookup(value)
            # update value only if value is a class
            if isclass(value):
                self.impl = None  # and nonify the impl
                self._cls = value
            else:  # raise TypeError if value is not a class
                raise TypeError('value {0} must be a class'.format(value))

        else:  # clean cls and impl
            self.impl = None  # nonify impl
            self._cls = None  # nonify cls

    @property
    def impl(self):
        """
        :return: self implementation.
        """
        return self._impl

    @impl.setter
    def impl(self, value):
        """Change of impl. Ensure self cls is consistent with input impl.

        :param value: new impl to use. If None, nonify cls as well.
        """

        # unapply business annotations on old impl
        if self._impl is not None:
            for component in self._rports:
                    CtlAnnotation.unapply_from(
                        component=component, impl=self._impl
                    )

        if value is not None:
            # update cls
            self._cls = value.__class__
            # and impl
            self._impl = value
            # apply business annotations on impl
            for component in self._rports:
                CtlAnnotation.apply_on(component=component, impl=self._impl)
                # and call setters then getters
                C2CtlAnnotation.call_setters(
                    component=component, impl=self._impl, call_getters=True
                )

        else:
            self._cls = None  # nonify cls
            self._impl = None  # nonify impl

    @staticmethod
    def get_stateful(component):
        """Get ImplController stateful from input component.

        :param Component component: component from where get stateful.
        :return: component implementation stateful status.
        :rtype: bool
        """

        result = None

        ictl = ImplController.get_ctl(component=component)
        if ictl is not None:
            result = ictl.stateful

        return result

    @staticmethod
    def set_stateful(component, stateful):
        """Set ImplController stateful from input component.

        :param Component component: component from where get stateful.
        """

        ictl = ImplController.get_ctl(component=component)
        if ictl is not None:
            ictl.stateful = stateful

    @staticmethod
    def get_cls(component):
        """Get ImplController cls from input component.

        :param Component component: component from where get class impl.
        :return: component implementation class.
        """

        result = None

        ictl = ImplController.get_ctl(component=component)
        if ictl is not None:
            result = ictl.cls

        return result

    @staticmethod
    def set_cls(component, cls):
        """Set ImplController cls from input component.

        :param Component component: component from where get class impl.
        """

        ictl = ImplController.get_ctl(component=component)
        if ictl is not None:
            ictl.cls = cls

    @staticmethod
    def get_impl(component):
        """Get ImplController impl from input component.

        :param Component component: component from where get impl.
        :return: component implementation.
        """

        result = None

        ictl = ImplController.get_ctl(component=component)
        if ictl is not None:
            result = ictl.impl

        return result

    @staticmethod
    def set_impl(component, impl):
        """Set ImplController impl from input component.

        :param Component component: component from where set impl.
        :param impl: new impl to use.
        """

        ictl = ImplController.get_ctl(component=component)
        if ictl is not None:
            ictl.impl = impl

    @staticmethod
    def instantiate_impl(component, args=None, kwargs=None):
        """Instantiate a new implementation.

        :param Component component: component from where renew the impl.
        :param list args: implementation instantation varargs.
        :param dict kwargs: implementation instantation keywords.
        :return: new impl.
        """

        result = None

        ictl = ImplController.get_ctl(component=component)
        if ictl is not None:
            result = ictl.instantiate(
                component=component, args=args, kwargs=kwargs
            )

        return result


def new_component(cls, *controllers):
    """Generate a component related to an input business cls and controller
    classes.

    :param type cls: class implementation.
    :param controllers: types of controllers to bind to the component.
    """

    result = Component()

    ictl = ImplController.bind_to(result)
    ictl.cls = cls

    for controller in controllers:
        controller.bind_to(result)

    ictl.instantiate()

    return result


class SetImplCtl(C2CtlAnnotation):
    """Annotation dedicated to inject an ImplController in an implementation.
    """

    def get_value(self, component, *args, **kwargs):

        return ImplController.get_ctl(component)


class Context(C2CtlAnnotation):
    """Annotation dedicated to inject a component into its implementation.
    """

    __slots__ = C2CtlAnnotation.__slots__

    def get_value(self, component, *args, **kwargs):

        return component


@MaxCount()
@Target(type)
class Stateless(CtlAnnotation):
    """Specify stateless on impl controller.
    """

    IMPL_STATEFUL = 'impl_stateful'  #: impl stateful attribute name

    __slots__ = (IMPL_STATEFUL, ) + CtlAnnotation.__slots__

    def apply(self, component, *args, **kwargs):
        # save old stateful status
        self.impl_stateful = ImplController.get_stateful(component=component)
        # change of stateful status
        ImplController.set_stateful(component=component, stateful=False)

    def unapply(self, component, *args, **kwargs):
        # recover old stateful status
        ImplController.set_stateful(
            component=component, stateful=self.impl_stateful
        )
