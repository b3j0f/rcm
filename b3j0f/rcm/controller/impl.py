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

try:
    from threading import Lock
except ImportError:
    from dummy_threading import Lock

from re import compile as re_compile

from inspect import isclass, getmembers, isroutine

from b3j0f.annotation import Annotation
from b3j0f.annotation.check import Target, MaxCount
from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup
from b3j0f.utils.proxy import get_proxy
from b3j0f.rcm.core import Component
from b3j0f.rcm.controller.core import Controller


class ImplController(Controller):
    """Impl Controller which uses a class in order to instantiate a component
    business implementation.
    """

    STATEFUL = 'stateful'  #: stateful property
    CLS = '_cls'  #: cls field name
    IMPL = '_impl'  #: impl field name

    __slots__ = (STATEFUL, CLS, IMPL) + Controller.__slots__

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
        # enrich params with ParameterizedImplAnnotations
        # get construtor
        constructor = getattr(
            self._cls, '__init__', getattr(self._cls, '__new__', None)
        )
        if constructor is not None:
            pias = ParameterizedImplAnnotation.get_annotations(
                constructor, ctx=self._cls
            )
            for pia in pias:
                # get value
                value = pia.get_resource(component=component)
                # get name
                name = pia.param
                if not name:  # if name is not given, add it into args
                    args.append(value)
                elif name not in kwargs:  # if name is given, add it to kwargs
                    kwargs[name] = value
        # save impl and result
        try:
            result = self.impl = self._cls(*args, **kwargs)
        except Exception as e:
            raise ImplController.ImplError(
                "Error ({0}) during impl instantiation of {1}".format(e, self)
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
        return self._impl

    @impl.setter
    def impl(self, value):
        """Change of impl. Ensure self cls is consistent with input impl.

        :param value: new impl to use. If None, nonify cls as well.
        """

        # unapply business annotations on old impl
        if self._impl is not None:
            for component in self.components:
                    ImplAnnotation.unapply_from(
                        component=component, impl=self._impl
                    )

        if value is not None:
            # update cls
            self._cls = value.__class__
            # and impl
            self._impl = value
            # apply business annotations on impl
            for component in self.components:
                ImplAnnotation.apply_on(component=component, impl=self._impl)

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
    def set_cls(component, cls):
        """Get ImplController cls from input component.

        :param Component component: component from where get class impl.
        """

        result = None

        ic = ImplController.get_controller(component=component)
        if ic is not None:
            ic.cls = cls

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
    def set_impl(component, impl):
        """Get ImplController impl from input component.

        :param Component component: component from where get impl.
        """

        result = None

        ic = ImplController.get_controller(component=component)
        if ic is not None:
            ic.impl = impl

        return result

    @staticmethod
    def instantiate_impl(component, args=None, kwargs=None):

        result = None

        ic = ImplController.get_controller(component=component)
        if ic is not None:
            result = ic.instantiate(
                component=component, args=args, kwargs=kwargs
            )

        return result


class ImplAnnotation(Annotation):
    """Annotation dedicated to Impl implementations.
    """

    def apply(self, component, impl, member=None):
        """Callback when Impl component renew its implementation.

        :param Component component: business implementation component.
        :param impl: component business implementation.
        :param member: business implementation member.
        """

        pass

    def unapply(self, component, impl, member=None):
        """Callback when Impl component change of implementation.

        :param Component component: business implementation component.
        :param impl: component business implementation.
        :param member: business implementation member.
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
                        annotation.apply(component=component, impl=impl)
                    else:
                        annotation.unapply(component=component, impl=impl)

            for name, member in getmembers(impl.__class__, lambda m: isroutine(m)):
                annotations = cls.get_annotations(member, ctx=impl.__class__)
                for annotation in annotations:
                    if check is None or check(annotation):
                        member = getattr(impl, name)
                        if _apply:
                            annotation.apply(
                                component=component, impl=impl, member=member
                            )
                        else:
                            annotation.unapply(
                                component=component, impl=impl, member=member
                            )

    @classmethod
    def apply_on(cls, component, impl=None, check=None):
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
    def unapply_from(cls, component, impl=None, check=None):
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

    def get_resource(self, component, impl=None, member=None):
        """Get a resource to inject in a routine call in the scope of a
        component, impl, prev_impl, member and prev_attr.

        :param Component component: business implementation component.
        :param impl: component business implementation.
        :param member: business implementation member.
        """

        return component

    def apply(self, component, impl, member=None, *args, **kwargs):

        # get the right resource to inject
        resource = self.get_resource(
            component=component, impl=impl, member=member
        )
        # identify the right target element to inject resource
        target = impl if member is None else member
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

    if result:  # lower result
        result = result.lower()

    return result


def getter_name(getter):
    """Get getter name.
    """

    return _accessor_name(getter, 'get')


def setter_name(setter):
    """Get setter name.
    """

    return _accessor_name(setter, 'set')


class Proxy(Component):
    """Base class for InputProxy and OutputProxy.

    Its role is to bind the component with the environment resources.

    It uses interfaces in order to describe what is promoted.
    """

    CMP_PORT_SEPARATOR = ':'  #: char separator between a component and port

    INTERFACES = '_interfaces'  #: interfaces field name
    _SOURCES = '_sources'  #: source proxy
    _LOCK = '_lock'  #: private lock field name

    __slots__ = (
        INTERFACES,  # public attributes
        _LOCK, _SOURCES  # private attributes
    ) + Component.__slots__

    def __init__(
        self, interfaces=None, sources=None, *args, **kwargs
    ):

        super(Proxy, self).__init__(*args, **kwargs)

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
        """Promote this port to input component proxy where names match with
        input sources.

        :param Component component: component from where find sources.
        :param sources: sources to promote.
        :type sources: list or str of type [port_name/]sub_port_name
        """

        #ensure sources are a list of str
        if isinstance(sources, basestring):
            sources = [sources]

        for source in sources:
            # first, identify component name with proxy
            splitted_source = source.split(Proxy.CMP_PORT_SEPARATOR)
            if len(splitted_source) == 1:
                # by default, search among the impl controller
                component_rc = re_compile(
                    '^{0}'.format(ImplController.ctrl_name())
                )
                port_rc = re_compile(splitted_source[0])
            else:
                component_rc = re_compile(splitted_source[0])
                port_rc = re_compile(splitted_source[1])

            proxy = self._component_cls().get_cls_proxy(
                component=component,
                select=lambda name, component:
                    component_rc.match(name)
                    and self._component_filter(name, component)
            )
            # bind port
            for name in proxy:
                port = proxy[name]
                if port_rc.match(name) and self._port_filter(name, port):
                    self[name] = port

    def _component_cls(self):

        return Component

    def _port_cls(self):

        return Proxy

    def _component_filter(self, name, component):

        return True

    def _port_filter(self, name, port):

        return True


class InputProxy(Proxy):
    """Input port.
    """

    __slots__ = Proxy.__slots__


class Input(ParameterizedImplAnnotation):
    """InputProxy injector which uses a name in order to inject a InputProxy.
    """

    NAME = 'name'  #: input port name field name

    __slots__ = (NAME, ) + ParameterizedImplAnnotation.__slots__

    def __init__(self, name, *args, **kwargs):

        super(Input, self).__init__(*args, **kwargs)

        self.name = name

    def get_port_name(self, *args, **kwargs):

        return self.name


class ProxyBinding(Component):
    """Proxy binding which describe the mean to promote component content.

    Such port binding has a name and a proxy.
    The proxy is generated thanks to the bound port interfaces and the content
    to promote.
    """

    NAME = 'name'  #: binding name field name
    PROXY = '_proxy'  #: proxy value field name

    __slots__ = (NAME, PROXY) + Component.__slots__

    def __init__(self, name, *args, **kwargs):

        super(ProxyBinding, self).__init__(*args, **kwargs)

        self.name = name

    def bind(self, component, port_name, *args, **kwargs):

        if isinstance(component, OutputProxy):

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

        if isinstance(component, OutputProxy):

            self.del_proxy()


class OutputProxy(Proxy):
    """Output port which provides component content thanks to port bindings.

    Those bindings are bound to the output port such as any component.
    """

    ASYNC = 'async'  #: asynchronous mode
    STATELESS = 'stateless'  #: stateless mode

    __slots__ = (ASYNC, STATELESS) + Proxy.__slots__

    def __init__(self, async=False, stateless=False, *args, **kwargs):

        super(OutputProxy, self).__init__(*args, **kwargs)

        self.async = async
        self.stateless = stateless

    def bind(self, component, port_name, *args, **kwargs):

        Output.apply(component=component)

    def unbind(self, component, port_name, *args, **kwargs):

        Output.unapply(component=component)


class Output(ParameterizedImplAnnotation):
    """Impl Out descriptor.
    """

    ASYNC = 'async'  #: asynchronous mode
    STATELESS = 'stateless'  #: stateless mode
    RESOURCE = '_resource'  #: output port resource field name

    __slots__ = (RESOURCE, ) + ParameterizedImplAnnotation.__slots__

    def __init__(self, async, stateless, resource, *args, **kwargs):

        self.resource = resource
        self.async = async
        self.stateless = stateless

    @property
    def resource(self):

        return self._resource

    @resource.setter
    def resource(self, value):

        if isinstance(value, basestring):
            value = lookup(value)

        self._resource = value


@MaxCount()
@Target(type)
class Stateless(ImplAnnotation):
    """Specify stateless on impl controller.
    """

    IMPL_STATEFUL = 'impl_stateful'  #: impl stateless attribute name

    __slots__ = (IMPL_STATEFUL, ) + ImplAnnotation.__slots__

    def apply(self, component, *args, **kwargs):

        self.impl_stateful = ImplController.get_stateful(component=component)
        ImplController.set_stateful(component=component, stateful=False)

    def unapply(self, component, *args, **kwargs):

        ImplController.set_stateful(
            component=component, stateful=self.impl_stateful
        )


@Target(type)
class Proxys(ImplAnnotation):
    """Annotation in charge of binding proxy in a component proxy.
    """

    PROXY = 'proxy'

    __slots__ = (PROXY, ) + ImplAnnotation.__slots__

    def __init__(self, proxy, *args, **kwargs):
        """
        :param proxy: proxy to bind to component.
        :type proxy: dict
        """
        super(Proxys, self).__init__(*args, **kwargs)

        self.proxy = proxy

    def apply(self, component, *args, **kwargs):

        # iterate on all self proxy
        self_proxy = self.proxy
        for port_name in self_proxy:
            port = self_proxy[port_name]
            # bind it with its name
            component[port_name] = port

    def unapply(self, component, *args, **kwargs):

        # iterate on all self proxy
        self_proxy = self.proxy
        for port_name in self_proxy:
            # bind it with its name
            del component[port_name]
