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
    # impl annotations
    'ImplAnnotation', 'Impl', 'ParameterizedImplAnnotation', 'Context',
    'getter_name', 'setter_name',  # util function
    'PropertyController',  # property controller
    'Property', 'GetProperty', 'SetProperty',  # property annotations
]

from b3j0f.annotation import Annotation
from b3j0f.annotation.check import Target
from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup
from b3j0f.rcm.core import Component
from b3j0f.rcm.controller.core import Controller

from inspect import isclass


class ImplController(Controller):
    """Impl Controller which uses a class in order to instantiate a component
    business implementation.
    """

    CLS = '_cls'  #: cls field name
    IMPL = '_impl'  #: impl field name

    __slots__ = (CLS, IMPL, ) + Controller.__slots__

    def __init__(self, cls=None, *args, **kwargs):
        """
        :param cls: class to use.
        :type cls: str or type
        :param dict named_ports: named ports.
        """

        super(ImplController, self).__init__(*args, **kwargs)

        self.cls = cls

    def renew_impl(self, component=None, cls=None, params=None):
        """Instantiate business element and returns it.

        Instantiation parameters depend on 3 levels of customisation in this
        order (related to a component-driven approach):

        - specific parameters ``params`` given in this method.
        - dynamic parameters given by the property controller.
        - dynamic parameters given by GetProperty annotations from cls and
        from cls constructor.

        :param cls: new cls to use. If None, use self.cls.
        :type cls: type or str
        :param dict params: new impl parameters which are specific to this impl
            and chosen instead of those ones from the property controller or
            GetProperty annotations.
        :return: new impl.
        """
        # init params.
        if params is None:
            params = {}
        # save prev impl
        prev_impl = self.impl
        # save cls
        self.cls = cls
        # get properties from the property controller and from the annotations
        if component is not None:
            # start to get params from property controller
            pc = PropertyController.get_controller(component=component)
            if pc is not None:
                # update params with the property controller
                for name in pc.properties:
                    # update params if property is not specified in params
                    if name not in params:
                        value = pc.properties[name]
                        params[name] = value
                # update params with GetProperty annotations
                # from cls
                gps = GetProperty.get_annotations(self._cls)
                for gp in gps:
                        param = gp.name if gp.param is None else gp.param
                        if param not in params:
                            params[param] = gps.params[gp.name]
                # and from the constructor
                try:
                    constructor = getattr(
                        self._cls, '__init__', getattr(
                            self._cls, '__new__'
                        )
                    )
                except AttributeError:
                    pass
                else:
                    gps = GetProperty.get_annotations(constructor)
                    for gp in gps:
                        param = gp.name if gp.param is None else gp.param
                        if param not in params:
                            params[param] = gps.params[gp.name]
        # save impl and result
        result = self.impl = self._cls(**params)
        # (un)apply business annotations on impl
        if isinstance(component, Component):
            ImplAnnotation.unapply(component=component, impl=prev_impl)
            ImplAnnotation.apply(component=component, impl=self.impl)

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
        # if value is a str, try to find the right class
        if isinstance(value, basestring):
            value = lookup(value)
        # update value only if value is a class
        if isclass(value):
            self._cls = value
            self._impl = None  # and nonify the impl
        else:  # raise TypeError if value is not a class
            raise TypeError('value {0} must be a class'.format(value))

    @property
    def impl(self):
        return self._impl

    @impl.setter
    def impl(self, value):

        # update cls
        self.cls = value.__class__
        # and impl
        self._impl = value

    @staticmethod
    def get_cls(cls, component):
        """Get ImplController cls from input component.

        :param Component component: component from where get class impl.
        """

        result = None

        ic = ImplController.get_controller(component=component)
        if ic is not None:
            result = ic.cls

        return result

    @staticmethod
    def get_impl(cls, component):
        """Get ImplController impl from input component.

        :param Component component: component from where get impl.
        """

        result = None

        ic = ImplController.get_controller(component=component)
        if ic is not None:
            result = ic.impl

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
    def _process(cls, component, impl=None, check=None, _apply=True):
        """Apply all cls annotations on component and impl.

        :param Component component: business implementation component.
        :param impl: component business implementation.
        :param check: check function which takes in parameter an annotation in
        order to do annotation.apply_on. If None, annotations are applied.
        """

        if impl is None:
            impl = ImplController.get_impl(component=component)

        if impl is not None:
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
    def apply(cls, component, impl=None, check=None):
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
    def unapply(cls, component, impl=None, check=None):
        """Unapply all cls annotations on component and impl.

        :param Component component: business implementation component.
        :param impl: component business implementation.
        :param check: check function which takes in parameter an annotation in
        order to do annotation.apply_on. If None, annotations are applied.
        """

        return cls._process(
            component=component, impl=impl, check=check, _apply=False
        )


@Target(type)
class Ports(ImplAnnotation):
    """Annotation in charge of binding ports in a component ports.
    """

    PORTS = 'ports'

    __slots__ = (PORTS, ) + ImplAnnotation.__slots__

    def __init__(self, ports, *args, **kwargs):
        """
        :param ports: ports to bind to component.
        :type ports: dict
        """
        super(Ports, self).__init__(*args, **kwargs)

        self.ports = ports

    def apply_on(self, component, *args, **kwargs):

        # iterate on all self ports
        self_ports = self.ports
        for port_name in self_ports:
            port = self_ports[port_name]
            # bind it with its name
            component[port_name] = port

    def unapply_on(self, component, *args, **kwargs):

        # iterate on all self ports
        self_ports = self.ports
        for port_name in self_ports:
            # bind it with its name
            del component[port_name]


class ParameterizedImplAnnotation(ImplAnnotation):
    """Abstract annotation which takes in parameter a param in order to inject
    a resource with a dedicated parameter name in a routine.
    """

    PARAM = 'param'  #: param field name

    __slots__ = (PARAM, ) + ImplAnnotation.__slots__

    def __init__(self, param=None, *args, **kwargs):

        super(Context, self).__init__(*args, **kwargs)

        self.param = param

    def get_resource(self, component, impl, attr=None):
        """Get a resource to inject in a routine call in the scope of a
        component, impl, prev_impl, attr and prev_attr.

        :param Component component: business implementation component.
        :param impl: component business implementation.
        :param attr: business implementation attribute.
        """

        return component

    def apply_on(self, component, impl, attr=None, *args, **kwargs):
        # get the right resource to inject
        resource = self.get_resource(component=component, impl=impl, attr=attr)
        # identify the right target element to inject resource
        target = impl if attr is None else attr
        # inject the resource in the target
        if self.param is None:
            try:
                target(resource)
            except TypeError:
                target()
        else:
            kwargs = {self.param: resource}
            target(**kwargs)


class Context(ParameterizedImplAnnotation):
    """Annotation dedicated to inject a port in a component implementation
    related to the method.
    """

    NAME = 'name'  #: port name field name

    __slots__ = (NAME, ) + ParameterizedImplAnnotation.__slots__

    def __init__(self, name, *args, **kwargs):

        super(Context, self).__init__(*args, **kwargs)

        self.name = name

    @property
    def name(self):

        return self._name

    @name.setter
    def name(self, value):

        self._name = value

    def get_resource(self, component, *args, **kwargs):

        # resource corresponds to a component port or the component if port
        # name does not exist
        port_name = self.name
        result = component if port_name is None else component[port_name]
        return result


class Impl(Context):
    """Annotation dedicated to inject an ImplController in an implementation.
    """

    __slots__ = Context.__slots__

    def __init__(self, name=ImplController.get_name(), *args, **kwargs):

        super(Impl, self).__init__(name=name, *args, **kwargs)


def _accessor_name(accessor, prefix):
    """Get accessor name which could contain prefix.
    """

    result = accessor.__name__

    if result.startswith(prefix):
        result = result[len(prefix):]
        if result and result[0] == '_':
            result = result[1:]

    return result


def getter_name(getter):
    """Get getter name.
    """

    return _accessor_name('get')


def setter_name(setter):
    """Get setter name.
    """

    return _accessor_name('set')


class PropertyController(Controller):
    """Dedicated to manage component parameters.
    """

    PROPERTIES = 'properties'  #: properties field name

    __slots__ = (PROPERTIES, ) + Controller.__slots__

    def __init__(self, properties=None, *args, **kwargs):

        super(PropertyController, self).__init__(*args, **kwargs)
        self.properties = {} if properties is None else properties


class Property(Context):
    """Inject a PropertyController in an implementation.
    """

    __slots__ = Context.__slots__

    def __init__(self, name=PropertyController.get_name(), *args, **kwargs):

        super(Property, self).__init__(name=name, *args, **kwargs)


class _PropertyAnnotation(ParameterizedImplAnnotation):

    NAME = 'name'  #: name field name

    __slots__ = (NAME, ) + ParameterizedImplAnnotation.__slots__

    def __init__(self, name, *args, **kwargs):

        super(_PropertyAnnotation, self).__init__(*args, **kwargs)

        self.name = name


class SetProperty(_PropertyAnnotation):
    """Set a property value from an implementation attr.
    """

    __slots__ = _PropertyAnnotation.__slots__

    def get_resource(self, component, attr, *args, **kwargs):

        pc = PropertyController.get_controller(component=component)

        if pc is not None:
            # get the right name
            name = setter_name(attr) if self.name is None else self.name
            # and the right property
            result = pc.properties[name]

        return result


class GetProperty(_PropertyAnnotation):
    """Get a property value from an implementation attr.
    """

    __slots__ = _PropertyAnnotation.__slots__

    def apply_on(self, component, attr, *args, **kwargs):

        pc = PropertyController.get_controller(component=component)

        if pc is not None:
            # get attr result
            value = attr()
            # get the right name
            name = getter_name(attr) if self.name is None else self.name
            # udate property controller
            pc.properties[name] = value
