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
]

from inspect import isclass

from b3j0f.annotation import Annotation
from b3j0f.annotation.check import Target
from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup
from b3j0f.rcm.core import Component
from b3j0f.rcm.controller.core import Controller

from re import compile as re_compile


class ImplController(Controller):
    """Impl Controller which uses a class in order to instantiate a component
    business implementation.
    """

    CLS = '_cls'  #: cls field name
    IMPL = '_impl'  #: impl field name
    #: private property module field name
    _PROPERTY = '_property'

    __slots__ = (CLS, IMPL, _PROPERTY) + Controller.__slots__

    def __init__(self, cls=None, impl=None, *args, **kwargs):
        """
        :param cls: class to use.
        :type cls: str or type
        :param impl: class implementation.
        :param dict named_ports: named ports.
        """

        super(ImplController, self).__init__(*args, **kwargs)

        # init private params
        self._impl = None
        self._cls = None
        # init cls
        self.cls = cls
        self.impl = impl
        # import property module
        import b3j0f.rcm.controller.property as prop
        self._property = prop

    def update(self, component=None, cls=None, params=None):
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
            pc = self._property.PropertyController.get_controller(
                component=component
            )
            if pc is not None:
                # update params with the property controller
                for name in pc.properties:
                    # update params if property is not specified in params
                    if name not in params:
                        value = pc.properties[name]
                        params[name] = value
                # update params with GetProperty annotations
                # from cls
                gps = self._property.GetProperty.get_annotations(self._cls)
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
                    gps = self._property.GetProperty.get_annotations(
                        constructor
                    )
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

        if value is not None:
            # if value is a str, try to find the right class
            if isinstance(value, basestring):
                value = lookup(value)
            # update value only if value is a class
            if isclass(value):
                self._cls = value
                self._impl = None  # and nonify the impl
            else:  # raise TypeError if value is not a class
                raise TypeError('value {0} must be a class'.format(value))

        else:  # clean cls and impl
            self._cls = None  # nonify cls
            self._impl = None  # nonify impl

    @property
    def impl(self):
        return self._impl

    @impl.setter
    def impl(self, value):

        if value is not None:
            # update cls
            self._cls = value.__class__
            # and impl
            self._impl = value

        else:
            self._cls = None  # nonify cls
            self._impl = None  # nonify impl

    @staticmethod
    def get_cls(component):
        """Get ImplController cls from input component.

        :param Component component: component from where get class impl.
        """

        result = None

        ic = ImplController.get_controller(component=component)
        if ic is not None:
            result = ic.cls

        return result

    @staticmethod
    def get_impl(component):
        """Get ImplController impl from input component.

        :param Component component: component from where get impl.
        """

        result = None

        ic = ImplController.get_controller(component=component)
        if ic is not None:
            result = ic.impl

        return result

    @staticmethod
    def update_impl(component, cls=None, params=None):

        result = None

        ic = ImplController.get_controller(component=component)
        if ic is not None:
            result = ic.update(component, cls, params)

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


class ParameterizedImplAnnotation(ImplAnnotation):
    """Abstract annotation which takes in parameter a param in order to inject
    a resource with a dedicated parameter name in a routine.
    """

    PARAM = 'param'  #: param field name

    __slots__ = (PARAM, ) + ImplAnnotation.__slots__

    def __init__(self, param=None, *args, **kwargs):

        super(ParameterizedImplAnnotation, self).__init__(*args, **kwargs)

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

    def __init__(self, name=ImplController.ctrl_name(), *args, **kwargs):

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


class Port(Component):
    """Base class for InputPort and OutputPort.

    Its role is to bind the component with the environment resources.

    It uses interfaces in order to describe what is promoted.
    """

    CMP_PORT_SEPARATOR = ':'  #: char separator between a component and port

    INTERFACES = '_interfaces'  #: interfaces field name
    _SOURCES = '_sources'  #: source ports
    _LOCK = '_lock'  #: private lock field name

    __slots__ = (
        INTERFACES,  # public attributes
        _LOCK, _SOURCES  # private attributes
    ) + Component.__slots__

    def __init__(
        self, interfaces=None, sources=None, *args, **kwargs
    ):

        super(Port, self).__init__(*args, **kwargs)

        self._lock = Lock()
        self.interfaces = interfaces
        self._sources = []
        self.sources = sources

    @property
    def interfaces(self):
        """Return an array of self interfaces
        """

        return [self._interfaces]

    @interfaces.setter
    def interfaces(self, value):
        """Update interfaces with a list of interface names/types.

        :param value:
        :type value: list or str
        """

        self._lock.acquire()

        # ensure interfaces are a set of types
        if isinstance(value, basestring):
            value = set([lookup(value)])
        elif isinstance(value, type):
            value = set([value])
        # convert all str to tuple of types
        self._interfaces = (
            v if isinstance(v, type) else lookup(v) for v in value
        )

        self._lock.release()

    def promote(self, component, sources):
        """Promote this port to input component ports where names match with
        input sources.

        :param Component component: component from where find sources.
        :param sources: sources to promote.
        :type sources: list or str of type [port_name/]sub_port_name
        """

        #ensure sources are a list of str
        if isinstance(sources, basestring):
            sources = [sources]

        for source in sources:
            # first, identify component name with ports
            splitted_source = source.split(Port.CMP_PORT_SEPARATOR)
            if len(splitted_source) == 1:
                # by default, search among the impl controller
                component_rc = re_compile(
                    '^{0}'.format(ImplController.ctrl_name())
                )
                port_rc = re_compile(splitted_source[0])
            else:
                component_rc = re_compile(splitted_source[0])
                port_rc = re_compile(splitted_source[1])

            ports = self._component_cls().get_cls_ports(
                component=component,
                select=lambda name, component:
                    component_rc.match(name)
                    and self._component_filter(name, component)
            )
            # bind port
            for name in ports:
                port = ports[name]
                if port_rc.match(name) and self._port_filter(name, port):
                    self[name] = port

    def _component_cls(self):

        return Component

    def _port_cls(self):

        return Port

    def _component_filter(self, name, component):

        return True

    def _port_filter(self, name, port):

        return True


class InputPort(Port):
    """Input port.
    """

    __slots__ = Port.__slots__


class Input(ParameterizedImplAnnotation):
    """InputPort injector which uses a name in order to inject a InputPort.
    """

    NAME = 'name'  #: input port name field name

    __slots__ = (NAME, ) + ParameterizedImplAnnotation.__slots__

    def __init__(self, name, *args, **kwargs):

        super(Input, self).__init__(*args, **kwargs)

        self.name = name

    def get_port_name(self, *args, **kwargs):

        return self.name


class PortBinding(Component):
    """Port binding which describe the mean to promote component content.

    Such port binding has a name and a proxy.
    The proxy is generated thanks to the bound port interfaces and the content
    to promote.
    """

    NAME = 'name'  #: binding name field name
    PROXY = '_proxy'  #: proxy value field name

    __slots__ = (NAME, PROXY) + Component.__slots__

    def __init__(self, name, *args, **kwargs):

        super(PortBinding, self).__init__(*args, **kwargs)

        self.name = name

    def bind(self, component, port_name, *args, **kwargs):

        if isinstance(component, OutputPort):

            self.update_proxy()

    def update_proxy(self, component, interfaces, name):
        """Renew a proxy.
        """

        self._lock.acquire()

        impl = ImplController.get_impl(component)

        if impl is not None:
            self._proxy = get_proxy(impl, interfaces)

        self._lock.release()

    def del_proxy(self):
        """Delete self proxy.
        """
        pass

    def unbind(self, component, port_name, *args, **kwargs):

        if isinstance(component, OutputPort):

            self.del_proxy()


class OutputPort(Port):
    """Output port which provides component content thanks to port bindings.

    Those bindings are bound to the output port such as any component.
    """

    __slots__ = Component.__slots__

    def bind(self, component, port_name, *args, **kwargs):

        Output.apply(component=component)

    def unbind(self, component, port_name, *args, **kwargs):

        Output.unapply(component=component)


class Output(ParameterizedImplAnnotation):
    """Impl Out descriptor.
    """

    RESOURCE = '_resource'  #: output port resource field name

    __slots__ = (RESOURCE, ) + ParameterizedImplAnnotation.__slots__

    def __init__(self, resource, *args, **kwargs):

        self.resource = resource

    @property
    def resource(self):

        return self._resource

    @resource.setter
    def resource(self, value):

        if isinstance(value, basestring):
            value = lookup(value)

        self._resource = value


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
