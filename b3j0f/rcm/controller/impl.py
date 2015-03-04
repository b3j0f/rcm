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
    'ImplAnnotation', 'B2CAnnotation', 'C2BAnnotation',
    'Context', 'Port', 'Impl',
    'Stateless',
    'getter_name', 'setter_name',
    'Bind', 'Unbind'
]

from inspect import isclass, getmembers, isroutine

from collections import Iterable

from b3j0f.annotation import Annotation
from b3j0f.annotation.check import Target, MaxCount
from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup
from b3j0f.aop import weave, unweave
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
        # try to instantiate the implementation
        try:
            result = C2BAnnotation.call_setter(
                component=component, impl=self._cls, args=args, kwargs=kwargs,
                force=True
            )
        except Exception as e:
            raise ImplController.ImplError(
                "Error ({0}) during impl instantiation of {1}".format(e, self)
            )
        else:  # update self impl
            try:
                self.impl = result
            except Exception as e:
                raise ImplController.ImplError(
                    "Error ({0}) while changing of impl of {1}".format(e, self)
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
                # and call setters then getters
                C2BAnnotation.call_setters(
                    component=component, impl=self._impl, call_getters=True
                )

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

            for name, member in getmembers(
                impl.__class__,
                lambda m: isroutine(m)
            ):
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


class B2CAnnotation(ImplAnnotation):
    """Business to Component annotation in order to inject implementation
    values to the component properties.

    It updates its result attribute related to its annotated impl routines.
    """

    #__slots__ = Annotation.__slots__

    class B2CError(Exception):
        """Handle B2CAnnotation errors.
        """

    def get_result(self, component, impl, member, result):
        """Callback method after calling the annotated implementation routine.

        :param Component component: implementation component.
        :param impl: implementation instance.
        :param routine member: called implementation member.
        :param result: method result.
        """

        raise NotImplementedError()

    @classmethod
    def call_getters(cls, component, impl):
        """Call impl getters of type cls.

        :param Component component: implementation component.
        :param impl: implementation instance.
        :raises: B2CAnnotation.B2CError in case of getter call error.
        """
        # parse members which are routine and not constructors
        for name, member in getmembers(
            impl,
            lambda m:
                isroutine(m)
                and
                getattr(m, '__name__', None) not in ['__init__', '__new__']
        ):
            # for each one, try to call setter annotations
            cls.call_getter(
                component=component, impl=impl, getter=member
            )

    @classmethod
    def call_getter(
        cls, component, impl, getter, args=None, kwargs=None, force=False
    ):
        """Call getter if it is annotated by cls.

        :param Component component: implementation component.
        :param impl: implementation instance or cls if getter is None.
        :param routine getter: getter to call if it is annotated.
        :param list args: args to use in calling the getter.
        :param dict kwargs: kwargs to use in calling the getter.
        :param bool force: force call even if no C2BAnnotation exist.
        :return: getter call if it is annotated by cls.
        """

        # init getter result
        result = None
        # get SetterImplAnnotations
        b2cas = cls.get_annotations(getter, ctx=impl)
        if b2cas or force:  # if getter has getter annotations ?
            # initialize args and kwargs
            if args is None:
                args = []
            if kwargs is None:
                kwargs = {}
            # call the getter and save the result
            result = getter(*args, **kwargs)
            for b2ca in b2cas:  # update args and kwargs with sias
                b2ca.get_result(
                    component=component,
                    impl=impl,
                    getter=getter,
                    result=result
                )
            # call the getter and save the result
            try:
                result = getter(*args, **kwargs)
            except Exception as e:
                raise B2CAnnotation.B2CError(
                    "Error ({0}) while calling {1} with {2}".format(
                        e, getter, (args, kwargs)
                    )
                )

        return result


class C2BAnnotation(ImplAnnotation):
    """Component to Business implementation to use in order to configurate the
    implementation component from the implementation.

    Set a method parameter values before calling it.
    """

    PARAM = 'param'  #: method params attribute name
    IS_PNAME = 'ispname'  #: ispname attribute name
    UPDATE = 'update'  #: update parameter attribute name

    #__slots__ = (PARAM, IS_PNAME, UPDATE) + Annotation.__slots__

    class C2BError(Exception):
        """Handle C2BAnnotation errors.
        """

    def __init__(
        self, param=None, ispname=False, update=False, *args, **kwargs
    ):
        """
        :param param: parameters to inject in a business routine. It can be of
        different types and also depends on ispname::

            - None: first setter parameter corresponds to self value.
            - str: if ispname, param is self parameter name which refers to a
            value, otherwise, param is a setter parameter name.
            - dict: set of setter parameter name, self parameter name.
            - list: if ispname, param is a list of self parameter name
            which refer to a list of values (of the same size), otherwise,
            param is a list of setter parameter names.

        :type param: NoneType, str, dict or Iterable
        :param bool ispname: If False (default), param is used such setter
        parameter names if not specified (when param is a list or a str),
        otherwise, param is self parameter names.
        :param bool update: if False (default), do not update existing
        parameters.
        """

        super(C2BAnnotation, self).__init__(*args, **kwargs)

        self.param = param
        self.ispname = ispname
        self.update = update

    @classmethod
    def call_setters(cls, component, impl, call_getters=False):
        """Call impl setters of type cls.

        :param Component component: implementation component.
        :param impl: implementation instance.
        :param bool call_getters: call getters at the end of processing.
        """

        if call_getters:
            values_by_members = {}

        # get members to parse (routines and not constructors)
        members = getmembers(
            impl,
            lambda m:
                isroutine(m)
                and
                getattr(m, '__name__', None) not in ['__init__', '__new__']
        )

        # parse members
        for name, member in members:
            # for each one, try to call setter annotations
            value = cls.call_setter(
                component=component, impl=impl, setter=member
            )
            if call_getters and value is not None:
                values_by_members[member] = value

        if call_getters:
            # parse members
            for name, member in members:
                if member in values_by_members:  # if value already exists
                    value = values_by_members[member]
                    # update value in all B2CAnnotations
                    b2cas = B2CAnnotation.get_annotations(member, ctx=impl)
                    for b2ca in b2cas:
                        b2ca.get_result(
                            component=component, impl=impl, member=member,
                            result=value
                        )
                else:  # execute the member and update B2CAnnotations
                    B2CAnnotation.call_getter(
                        component=component, impl=impl, getter=member
                    )

    @classmethod
    def call_setter(
        cls, component, impl, setter=None, args=None, kwargs=None, force=False
    ):
        """Call setter if it is annotated by cls.

        If setter is None, use impl such as the setter.

        :param Component component: implementation component.
        :param impl: implementation instance or cls if setter is None.
        :param routine setter: setter to call if it is annotated.
        :param list args: args to use in calling the setter.
        :param dict kwargs: kwargs to use in calling the setter.
        :param bool force: force call even if no C2BAnnotation exist.
        :return: setter call if it is annotated by cls.
        """

        # init setter result
        result = None
        # get the right target
        if setter is None:
            target = getattr(impl, '__init__', getattr(impl, '__new__', impl))
            setter = impl
        else:
            target = setter
        # get SetterImplAnnotations
        c2bas = cls.get_annotations(target, ctx=impl)
        if c2bas or force:  # if setter has setter annotations ?
            # initialize args and kwargs
            if args is None:
                args = []
            if kwargs is None:
                kwargs = {}
            for c2ba in c2bas:  # update args and kwargs with sias
                c2ba._update_params(
                    component=component, impl=impl, member=setter,
                    args=args, kwargs=kwargs
                )
            # call the target and save the result
            try:
                result = setter(*args, **kwargs)
            except Exception as e:
                raise C2BAnnotation.C2BError(
                    "Error ({0}) while calling {1} with {2}".format(
                        e, setter, (args, kwargs)
                    )
                )

        return result

    def _update_params(self, component, impl, member, args, kwargs, **ks):
        """Update member call parameters.

        :param Component component: implementation component.
        :param impl: implementation instance.
        :param routine member: called member.
        :param list args: member call var args.
        :param dict kwargs: member call keywords.
        """

        param = self.param
        if param is None:  # append default value to args
            value = self.get_value(
                component=component, impl=impl, member=member,
                **ks
            )
            args.append(value)
        elif isinstance(param, basestring):  # if param is a str
            value = self.get_value(
                component=component, impl=impl, member=member,
                pname=param if self.ispname else None,
                **ks
            )
            if self.ispname:  # if param is a parameter name
                # put value in kwargs
                args.append(value)
            # else if param is a routine keyword argument
            elif self.update or param not in kwargs:
                # do nothing if update and param already in kwargs
                # value is in vararg
                kwargs[param] = value
        elif isinstance(param, dict):  # contains both arg names and values
            update = self.update
            for kwarg in param:
                # do nothing if update and param already in kwargs
                if update or kwarg not in kwargs:
                    pname = param[kwarg]
                    value = self.get_value(
                        component=component, impl=impl, member=member,
                        pname=pname,
                        **ks
                    )
                    kwargs[kwarg] = value
        elif isinstance(param, Iterable):  # contains dynamic values to put
            values = [None] * len(param)
            for index, pname in enumerate(param):
                value = self.get_value(
                    component=component,
                    impl=impl,
                    member=member,
                    pname=pname if self.ispname else None,
                    **ks
                )
                values[index] = value
            if self.ispname:
                args += values
            else:
                names_w_value = zip(param, values)
                update = self.update
                for name, value in names_w_value:
                    if update or name not in kwargs:
                        kwargs[name] = value

    def get_value(self, component, impl, member=None, pname=None, **ks):
        """Get value parameter.

        :param Component component: implementation component.
        :param impl: implementation instance.
        :param member: implementation member.
        :param str pname: parameter name. If None, result is component. Else,
        result is related component port which matches the port.
        """

        result = None

        if pname is None:  # if pname is None, return component
            result = component
        elif isinstance(pname, basestring):  # if str, return port component
            result = component.get(pname)
        elif isinstance(pname, Iterable):  # if iterable, return all get_values
            result = [
                self.get_value(
                    component=component,
                    impl=impl,
                    member=member,
                    pname=name,
                    **ks
                ) for name in pname
            ]

        return result


class C2B2CAnnotation(C2BAnnotation, B2CAnnotation):
    """Behaviour of both C2BAnnotation and B2CAnnotation.
    """


class Context(C2BAnnotation):
    """Annotation dedicated to inject a component into its implementation.
    """

    __slots__ = C2BAnnotation.__slots__

    def __init__(self, *args, **kwargs):

        super(Context, self).__init__(
            param=None, ispname=False, *args, **kwargs
        )


class Port(C2BAnnotation):
    """Annotation dedicated to inject a port in a component implementation.

    Value(s) to set depends on ``param``::

        - None: value is the component.
        - str: param is the port name.
        - list: params are port names.
        - dict: keys are parameters and values are port names.
    """

    __slots__ = C2BAnnotation.__slots__

    def __init__(self, param, ispname=True, *args, **kwargs):

        super(Port, self).__init__(
            param=param, ispname=ispname, *args, **kwargs
        )


class Ctrl2BAnnotation(C2BAnnotation):
    """Annotation dedicated to inject a component controller into its component
    implementation.
    """

    FORCE = 'force'  #: force attribute name.
    ERROR = 'error'  #: error attribute name.

    __slots__ = (FORCE, ) + C2BAnnotation.__slots__

    def __init__(self, param=None, force=False, error=None, *args, **kwargs):
        """
        :param bool force: force controller creation if not exists.
        :param type error: Error to raise if controller does not exist. If None
            (default) do not raise an error.
        """

        # avoid to define ispname is True
        super(Ctrl2BAnnotation, self).__init__(
            param=param, ispname=False, *args, **kwargs
        )

        self.force = force
        self.error = error

    def get_ctrl_cls(self):
        """Get ctrl cls.

        Must be overriden.
        :raises: NotImplementedError by default.
        """

        raise NotImplementedError()

    def get_value(self, component, impl, member=None, pname=None, **ks):

        result = None

        # get both controller class and name
        ctrl_cls = self.get_ctrl_cls()
        ctrl_name = ctrl_cls.ctrl_name()
        # get related controller
        result = component.get(ctrl_name)
        # if controller is None and self force creation of controller
        if result is None:
            if self.force:
                # get a new controller
                result = ctrl_cls.bind_to(components=component)
            elif self.error:
                raise self.error(
                    "Impossible to set {0}, controller {1} not bound to {2}"
                    .format(member, ctrl_cls, component)
                )

        return result


class Impl(Ctrl2BAnnotation):
    """Annotation dedicated to inject an ImplController in an implementation.
    """

    __slots__ = Ctrl2BAnnotation.__slots__

    def get_ctrl_cls(self):

        return ImplController


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


class C2BAnnotationInterceptor(C2BAnnotation):
    """C2B annotation dedicated to intercept context methods and to set
    corresponding methods in implementation.

    Implementation setters can be fired before, after or both.
    """

    BEFORE = 1  #: before flag value
    AFTER = 2  #: after flag value
    BOTH = BEFORE + AFTER  #: before and after flag values

    WHEN = 'when'  #: when attribute name

    def __init__(self, when=BOTH, *args, **kwargs):

        super(C2BAnnotationInterceptor, self).__init__(*args, **kwargs)

        self.when = when

    def get_target_ctx(self, *args, **kwargs):
        """Get target and ctx related to apply/unapply calls.

        :return: target and ctx.
        :rtype: tuple
        """

        raise NotImplementedError()

    def advice(self, joinpoint):

        component = joinpoint.kwargs.get('component')

        if self.when & C2BAnnotationInterceptor.BEFORE:
            for target in self.targets:
                impl = target.__self__
                args, kwargs = [], {}
                self._update_params(
                    component=component,
                    impl=impl,
                    member=target,
                    args=args,
                    kwargs=kwargs,
                    joinpoint=joinpoint
                )
                target(*args, **kwargs)

        joinpoint.proceed()

        if self.when & C2BAnnotationInterceptor.AFTER:
            for target in self.targets:
                impl = target.__self__
                args, kwargs = [], {}
                self._update_params(
                    component=component,
                    impl=impl,
                    member=target,
                    args=args,
                    kwargs=kwargs,
                    joinpoint=joinpoint
                )
                target(*args, **kwargs)

    def apply(self, *args, **kwargs):

        target, ctx = self.get_target(*args, **kwargs)

        weave(target, advices=self.advice, ctx=ctx)

    def unapply(self, *args, **kwargs):

        target, ctx = self.get_target(*args, **kwargs)

        unweave(target, advices=self.advice, ctx=ctx)


class Bind(C2BAnnotationInterceptor):
    """Called when a port is bound to component.
    """

    def get_target_ctx(self, component, *args, **kwargs):

        return component.__setitem__, component

    def get_value(self, joinpoint, *args, **kwargs):

        key = joinpoint.kwargs['key']
        item = joinpoint.kwargs.get('item')
        when = self.when

        return key, item, when


class Unbind(C2BAnnotation):
    """Called when a port is unbound from component.
    """

    def get_target_ctx(self, component, *args, **kwargs):

        return component.__delitem__, component

    def get_value(self, component, joinpoint, *args, **kwargs):

        key = joinpoint.kwargs['key']
        item = component.get('key')
        when = self.when

        return key, item, when
