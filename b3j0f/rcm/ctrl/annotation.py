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

"""Regroup base annotations to ensure dependency injection of controller
components.
"""

__all__ = [
    # abstract annotations
    'CtrlAnnotation', 'Ctrl2CAnnotation', 'C2CtrlAnnotation',
    'C2Ctrl2CAnnotation', 'CtrlAnnotationInterceptor',
    'Controllers',  # Controller annotation
    'Port', 'SetPort', 'RemPort',  # impl controller annotations
    'getter_name', 'setter_name'
]

from inspect import getmembers, isroutine, getargspec

from collections import Iterable

from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup
from b3j0f.aop import weave
from b3j0f.annotation import Annotation
from b3j0f.annotation.check import Target


class CtrlAnnotation(Annotation):
    """Annotation dedicated to do IoC and DI in controller implementation.
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
    def _process(cls, component, impl, check=None, _apply=True):
        """Apply all cls annotations on component and impl.

        :param Component component: component.
        :param impl: component business implementation.
        :param check: check function which takes in parameter an annotation in
        order to do annotation.apply_on. If None, annotations are applied.
        """

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
    def apply_on(cls, component, impl, check=None):
        """Apply all cls annotations on component and impl.

        :param Component component: controller component.
        :param impl: controller implementation.
        :param check: check function which takes in parameter an annotation in
        order to do annotation.apply_on. If None, annotations are applied.
        """

        return cls._process(
            component=component, impl=impl, check=check, _apply=True
        )

    @classmethod
    def unapply_from(cls, component, impl, check=None):
        """Unapply all cls annotations on component and impl.

        :param Component component: controller component.
        :param impl: controller implementation.
        :param check: check function which takes in parameter an annotation in
        order to do annotation.apply_on. If None, annotations are applied.
        """

        return cls._process(
            component=component, impl=impl, check=check, _apply=False
        )


@Target(type)
class Controllers(CtrlAnnotation):
    """Annotation dedicateed to bind several Controller classes on a component.
    """

    def __init__(self, controllers, *args, **kwargs):
        """
        :param controllers: controllers to bind to an implementation.
        """

        if not isinstance(controllers, list):
            controllers = list(controllers)

        controllers = [
            lookup(controller) if isinstance(controller, basestring)
            else controller
            for controller in controllers
        ]

    def apply(self, component, *args, **kwargs):

        for controller in self.controllers:
            controller.bindto(component=component)

    def unapply(self, component, *args, **kwargs):

        for controller in self.controllers:
            controller.unbindfrom(component=component)


class Ctrl2CAnnotation(CtrlAnnotation):
    """Controller to Component annotation in order to inject implementation
    values to the component properties.

    It updates its result attribute related to its annotated impl routines.
    """

    class Error(Exception):
        """Handle Ctrl2CAnnotation errors.
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
        :raises: Ctrl2CAnnotation.Error in case of getter call error.
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
        :param bool force: force call even if no C2CtrlAnnotation exist.
        :return: getter call if it is annotated by cls.
        """

        # init getter result
        result = None
        # get Ctrl2CAnnotations
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
                raise Ctrl2CAnnotation.Error(
                    "Error ({0}) while calling {1} with {2}".format(
                        e, getter, (args, kwargs)
                    )
                )

        return result


class C2CtrlAnnotation(CtrlAnnotation):
    """Component to Controller annotation to use in order to configurate
    the controller from the component.

    Set a method parameter values before calling it.
    """

    PARAM = 'param'  #: method params attribute name
    IS_PNAME = 'ispname'  #: ispname attribute name
    UPDATE = 'update'  #: update parameter attribute name

    class C2CtrlError(Exception):
        """Handle C2CtrlAnnotation errors.
        """

    def __init__(
        self, param=None, ispname=False, update=False, *args, **kwargs
    ):
        """
        :param param: parameters to inject in a controller routine. It can be
        of different types and also depends on ispname::

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

        super(C2CtrlAnnotation, self).__init__(*args, **kwargs)

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
                    # update value in all Ctrl2CAnnotations
                    b2cas = Ctrl2CAnnotation.get_annotations(member, ctx=impl)
                    for b2ca in b2cas:
                        b2ca.get_result(
                            component=component, impl=impl, member=member,
                            result=value
                        )
                else:  # execute the member with all Ctrl2CAnnotations
                    Ctrl2CAnnotation.call_getter(
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
        :param bool force: force call even if no C2CtrlAnnotation exist.
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
        # get Ctrl2CAnnotations
        c2nfas = cls.get_annotations(target, ctx=impl)
        if c2nfas or force:  # if setter has setter annotations ?
            # initialize args and kwargs
            if args is None:
                args = []
            if kwargs is None:
                kwargs = {}
            for c2nfa in c2nfas:  # update args and kwargs with sias
                c2nfa._update_params(
                    component=component, impl=impl, member=setter,
                    args=args, kwargs=kwargs
                )
            # call the target and save the result
            try:
                result = setter(*args, **kwargs)
            except Exception as e:
                raise C2CtrlAnnotation.C2CtrlError(
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
                component=component, impl=impl, member=member, _upctx={},
                **ks
            )
            args.append(value)
        elif isinstance(param, basestring):  # if param is a str
            value = self.get_value(
                component=component, impl=impl, member=member,
                pname=param if self.ispname else None, _upctx={},
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
            # initialize a new ctx related to self setter
            ctx = {}
            for kwarg in param:
                # do nothing if update and param already in kwargs
                if update or kwarg not in kwargs:
                    pname = param[kwarg]
                    value = self.get_value(
                        component=component, impl=impl, member=member,
                        pname=pname,
                        _upctx=ctx,
                        **ks
                    )
                    kwargs[kwarg] = value
        elif isinstance(param, Iterable):  # contains dynamic values to put
            values = [None] * len(param)
            # initialize a new ctx related to self setter
            ctx = {}
            for index, pname in enumerate(param):
                value = self.get_value(
                    component=component,
                    impl=impl,
                    member=member,
                    pname=pname if self.ispname else None,
                    _upctx=ctx,
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

    def get_value(
        self, component, impl, _upctx, member=None, pname=None, **ks
    ):
        """Get value parameter.

        :param Component component: implementation component.
        :param impl: implementation instance.
        :param dict _upctx: dictionary dedicated to manage shared values among
            several call of self.get_value in the same execution of
            self._update_params.
        :param member: implementation member.
        :param str pname: parameter name. If None, result is component. Else,
            result is related component port which matches the port.
        :return: value parameter.
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
                    _upctx=_upctx,
                    **ks
                ) for name in pname
            ]

        return result


class C2Ctrl2CAnnotation(C2CtrlAnnotation, Ctrl2CAnnotation):
    """Behaviour of both C2CtrlAnnotation and Ctrl2CAnnotation.
    """


class Port(C2CtrlAnnotation):
    """Annotation dedicated to inject a port in a component implementation.

    Value(s) to set depends on ``param``::

        - None: value is the component.
        - str: param is the port name.
        - list: params are port names.
        - dict: keys are parameters and values are port names.
    """

    __slots__ = C2CtrlAnnotation.__slots__

    def __init__(self, param, *args, **kwargs):

        super(Port, self).__init__(
            param=param, ispname=True, *args, **kwargs
        )


class CtrlAnnotationInterceptor(CtrlAnnotation):
    """C2B annotation dedicated to intercept context methods and to set
    corresponding methods in implementation.

    Implementation setters can be fired before, after or both.

    It is possible to specify intercepted parameters to bind to interception
    parameters with both varargs and kwargs respectively named ``vparams`` and
    ``kparams``. For example, if you want to retrieve the interception moment
    among (before, after) and the intercepted result, you can ask to get back
    the 'when' and 'result' parameter values in several ways such as:

    - vparams=['when', 'result']
    - kparams={'when': 'interception param name', 'result': '...'}
    """

    BEFORE = 1 << 0  #: before flag value.
    AFTER = 1 << 1  #: after flag value.
    BOTH = BEFORE | AFTER  #: before and after flag values.

    WHEN = 'when'  #: when attribute/parameter name.
    RESULT = 'result'  #: interception result parameter name.

    PARAMS = 'params'  #: parameters to put in the interceptor

    class Error(Exception):
        """Handle CtrlAnnotationInterceptor Errors.
        """

    def __init__(
        self, when=AFTER, vparams=None, kparams=None, *args, **kwargs
    ):
        """
        :param int when: when property (default AFTER)
        :param vparams: intercepted param name(s) to put in the
            interception parameters.
        :type vparams: list or str
        :param dict kparams: dict of (str, str) where keys are intercepted
        param names and values are interception param names.
        """

        super(CtrlAnnotationInterceptor, self).__init__(*args, **kwargs)

        self.when = when

        self.vparams = (
            [] if vparams is None else [vparams]
            if isinstance(vparams, basestring) else vparams
        )
        self.kparams = {} if kparams is None else kparams

    def _get_params(
        self, component, impl, member, joinpoint, when, argspec, result=None
    ):
        """Get right args and kwargs related to self vparams and kparams.

        :param Component component: intercepted component.
        :param impl: intercepted impl.
        :param member: interception member.
        :param b3j0f.aop.Joinpoint joinpoint: interception joinpoint.
        :param int when: interception moment.
        :param result: interception result if when is AFTER.
        :param tuple argspec: member argspec.

        :return: both interception args and kwargs.
        :rtype: tuple
        """

        # get args
        args = [
            self._get_param(
                name=name,
                component=component,
                impl=impl,
                member=member,
                joinpoint=joinpoint,
                when=when,
                result=result,
                argspec=argspec
            )
            for name in self.vparams
        ]
        # and kwargs
        kwargs = {}
        for intercepted_param in self.kparams:
            interception_param = self.kparams[intercepted_param]
            kwargs[interception_param] = self._get_param(
                name=intercepted_param,
                component=component,
                impl=impl,
                member=member,
                joinpoint=joinpoint,
                when=when,
                result=result,
                argspec=argspec
            )

        return args, kwargs

    def _get_param(
        self, name, component, impl, member, joinpoint, when, result, argspec
    ):
        """Get specific param value related to input parameters.

        :param Component component: intercepted component.
        :param impl: intercepted impl.
        :param member: interception member.
        :param b3j0f.aop.Joinpoint joinpoint: interception joinpoint.
        :param int when: interception moment.
        :param result: interception result if when is AFTER.
        :param tuple argspec: member argspec.

        :return: specific parameter.
        :raises: CtrlAnnotationInterceptor.Error if parameter value does
            not exist.
        """

        if name == CtrlAnnotationInterceptor.WHEN:
            result = when
        elif name == 'component':
            result = component
        elif name == 'impl':
            result = impl
        elif name == 'joinpoint':
            result = joinpoint
        elif name == 'result':  # do nothing if result is asked
            pass
        elif name in joinpoint.kwargs:  # check among joinpoint kwargs
            result = joinpoint.kwargs[name]
        elif name in argspec.args:  # check among joinpoint args
            index = argspec.args.index(name)
            result = joinpoint.args[index]

        else:  # if name is not handled, raise an Error
            raise CtrlAnnotationInterceptor.Error(
                "Wrong parameter name '{0}' in {1} ({2}).".format(
                    name, member, component
                )
            )

        return result

    def _get_advice(self, component, impl, member):
        """Get an advice able to proceed impl member.

        :param Component component: advice component.
        :param impl: component implementation.
        :param member: adviced member.
        :return: impl member advice.
        """

        argspec = getargspec(member)

        def advice(joinpoint):

            if self.when & CtrlAnnotationInterceptor.BEFORE:
                args, kwargs = self._get_params(
                    component=component,
                    impl=impl,
                    member=member,
                    joinpoint=joinpoint,
                    when=CtrlAnnotationInterceptor.BEFORE,
                    argspec=argspec
                )
                try:  # catch any exception
                    member(*args, **kwargs)
                except Exception:
                    pass

            result = joinpoint.proceed()

            if self.when & CtrlAnnotationInterceptor.AFTER:
                args, kwargs = self._get_params(
                    component=component,
                    impl=impl,
                    member=member,
                    joinpoint=joinpoint,
                    when=CtrlAnnotationInterceptor.AFTER,
                    result=result,
                    argspec=argspec
                )
                try:  # catch any exception
                    member(*args, **kwargs)
                except Exception:
                    pass

            return result

        return advice

    def get_target_ctx(self, *args, **kwargs):
        """Get target and ctx related to apply/unapply calls.

        :return: couple of (target, ctx).
        :rtype: tuple
        """

        raise NotImplementedError()

    def apply(self, component, impl, member, *args, **kwargs):

        target, ctx = self.get_target_ctx(
            component=component, impl=impl, member=member, *args, **kwargs
        )

        advice = self._get_advice(
            component=component, impl=impl, member=member
        )

        weave(target, advices=advice, ctx=ctx)


class SetPort(CtrlAnnotationInterceptor):
    """Called when a port is bound to component.

    Specific parameters are Component.set_port parameters:

    - name: new port name.
    - port: new port.
    """

    def get_target_ctx(self, component, *args, **kwargs):

        return component.set_port, component


class RemPort(CtrlAnnotationInterceptor):
    """Called when a port is unbound from component.

    Specific parameters are Component.remove_port parameters:

    - name: port name to remove.
    """

    def get_target_ctx(self, component, *args, **kwargs):

        return component.remove_port, component


def _accessor_name(accessor, prefix):
    """Get accessor name which could contain prefix.

    :param accessor: function from where get name.
    :param str prefix: name prefix.
    :return: accessor name.
    :rtype: str
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

    A getter name respects this format: let the getter named ``test``.
    The getter name can be ``gettest`` or ``get_test``.

    :param getter: getter function where name respects formats ``getX`` or
        ``get_X`` and result is ``X``.
    :return: getter name.
    :rtype: str
    """

    return _accessor_name(getter, 'get')


def setter_name(setter):
    """Get setter name.

    A setter name respects this format: let the setter named ``test``.
    The setter name can be ``gettest`` or ``get_test``.

    :param setter: setter function where name respects formats ``getX`` or
        ``get_X`` and result is ``X``.
    :return: setter name.
    :rtype: str
    """

    return _accessor_name(setter, 'set')
