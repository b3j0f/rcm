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

"""This module provides classes in charge of proxifying resources around
components.

It becomes easier to separate resources from the mean of providing/consuming
them.

Such operations are granted through the proxy design pattern in order to
separate ``what`` and ``how`` a component is bound/provided with its
environment.

The ``what`` is specified through the Port class. This one uses interfaces in
order to describe bound resources. The ``how`` is ensured with Binding objects
which are used by Port objects.
"""

__all__ = [
    'SetIOCtl', 'Input', 'Output', 'Async', 'Ports'
]

from inspect import isclass, isroutine

from b3j0f.annotation.check import Target, MaxCount
from b3j0f.rcm.ctl.annotation import (
    CtlAnnotationInterceptor, getter_name, setter_name
)
from b3j0f.rcm.ctl.annotation import (
    CtlAnnotation, Ctl2CAnnotation, C2CtlAnnotation
)
from b3j0f.rcm.io.port import Port
from b3j0f.rcm.io.ctl import IOController


class Input(CtlAnnotationInterceptor):
    """InputPort injector which uses a name in order to inject an InputPort
    proxy.
    """

    class Error(Exception):
        """Handle Input errors.
        """

    DEFAULT_MANDATORY = False  #: default mandatory
    DEFAULT_IOKIND = Port.INPUT  #: default port kind
    DEFAULT_MULTIPLE = Port.MULTIPLE  #: default multiple value
    DEFAULT_INF = Port.INF  #: default inf value
    DEFAULT_SUP = Port.SUP  #: default sup value

    NAME = 'name'  #: input port name field name
    MANDATORY = 'mandatory'  #: input port mandatory field name
    ITFS = 'itfs'  #: interfaces attribute name
    IOKIND = 'iokind'  #: i/o kind of port (input/output/both)
    MULTIPLE = 'multiple'  #: multiple port proxy attribute name
    INF = 'inf'  #: minimal number of bindable resources attribute name
    SUP = 'sup'  #: maximal number of bindable resources attribute name
    POLICYRULES = 'policyrules'  #: policy rules attribute name

    def __init__(
            self, name=None, mandatory=DEFAULT_MANDATORY,
            itfs=None, multiple=DEFAULT_MULTIPLE, iokind=DEFAULT_IOKIND,
            inf=DEFAULT_INF, sup=DEFAULT_SUP, policyrules=None,
            *args, **kwargs
    ):
        """
        :param str name: port name to retrieve. Default is annotated name.
        :param bool mandatory: if mandatory (default False) and port does not
            already exists, raise an Error. Otherwise, if the port is not
            created, creates it.
        :param itfs: port interfaces to use.
        :param bool multiple: port multiple attribute. Default is
            Port.DEFAULT_MULTIPLE.
        :param int iokind: port iokind attribute. Default is Port.INPUT.
        :param int int: port inf attribute. Default is Port.DEFAULT_INF.
        :param int sup: port sup attribute. Default is Port.DEFAULT_SUP.
        :param policyrules: port policyrules.
        """

        super(Input, self).__init__(*args, **kwargs)

        self.name = name
        self.mandatory = mandatory
        self.itfs = itfs
        self.multiple = multiple
        self.iokind = iokind
        self.inf = inf
        self.sup = sup
        self.policyrules = policyrules

    def get_target_ctx(self, component, member, *args, **kwargs):

        # get port name
        name = self._get_port_name(member)
        # get port
        port = component.get(name)
        # if port does not exist, instantiate it
        if port is None:
            port = Port(
                iokind=self.iokind,
                itfs=self.itfs,
                multiple=self.multiple,
                inf=self.inf,
                sup=self.sup,
                policyrules=self.policyrules
            )
            # and bind it to the component
            component.set_port(name=name, port=port)
        # target is the port renewproxy method
        target = None if port is None else port._renewproxy
        # result is the tuple of target (member) and port (ctx)
        result = target, port

        return result

    def _get_advice(self, component, member, *args, **kwargs):

        result = super(Input, self)._get_advice(*args, **kwargs)

        # if port proxy is None and self.mandatory
        if result is None and self.mandatory:
            # get port name
            name = self._get_port_name(member=member)
            # raise an error
            raise Input.Error(
                "Mandatory input {0} does not exists on {1} in component {2}"
                .format(name, member, component)
            )

        return result

    def _get_port_name(self, member):
        """get port name from self attributes or from the member.

        :param routine member: member from where get port name if self name
            is not given.
        :return: port name.
        :rtype: str
        """

        return getter_name(member) if self.name is None else self.name


class Output(Ctl2CAnnotation):
    """Output descriptor which automatically creates a port if related output
    port does not exist in the component.
    """

    STATELESS = 'stateless'  #: port stateless mode
    ITFS = 'itfs'  #: port itfs
    POLICYRULES = 'policyrules'  #: port policyrules
    IOKIND = 'iokind'  #: port iokind

    DEFAULT_IOKIND = Port.OUTPUT  #: default port iokind

    def __init__(
            self, name=None, stateless=False, itfs=None,
            policyrules=None, iokind=DEFAULT_IOKIND,
            *args, **kwargs
    ):
        """
        :param str name: output port name.
        :param bool stateless: stateless if True (False by default).
        :param tuple itfs: port itfs.
        :param PolicyRules policyrules: port policyrules.
        """

        super(Output, self).__init__(*args, **kwargs)

        self.name = name
        self.stateless = stateless
        self.itfs = itfs
        self.policyrules = policyrules
        self.iokind = iokind

    def process_result(
        self, result, component, member, target, *args, **kwargs
    ):

        # get port name
        name = self.name
        if name is None:  # get member name
            if isroutine(member):  # from a routine
                name = setter_name(member)
            elif isclass(member):  # from a class
                name = member.__name__.lower()
            else:
                raise RuntimeError("member must be a routine or a class.")

        # get itfs
        itfs = self.itfs
        if itfs is None:  # if itfs is not given, use annotation target
            itfs = target

        # get related port
        port = component.get(name)
        if port is None:
            # create a port
            port = Port(
                resource=result, itfs=self.itfs,
                policyrules=self.policyrules, iokind=self.iokind
            )
            # and bind it to the component
            component.set_port(port=port, name=name)
        else:  # update port properties
            port.resource = result
            port.itfs = itfs
            port.policyrules = self.policyrules
            port.iokind = self.iokind


@MaxCount()
@Target([Target.ROUTINE, type])
class Async(Ctl2CAnnotation):
    """Specify asynchronous mode on class methods.
    """

    def __init__(self, name=None, *args, **kwargs):
        """
        :param str name: specific port name.
        """

        super(Async, self).__init__(*args, **kwargs)

        self.name = name

    def process_result(self, result, component, getter, *args, **kwargs):

        getter_name = getter.__name__
        # create a port and bind it to the component
        port = Port.GET_PORTS(component=component, names=self.name)
        apply_policy(port.policyrules)


@Target(type)
class Ports(CtlAnnotation):
    """Annotation in charge of binding Port in a component Port.
    """

    Port = 'Port'

    #__slots__ = (Port, ) + CtlAnnotation.__slots__

    def __init__(self, port, *args, **kwargs):
        """
        :param dict port: port to bind to component.
        """

        super(Ports, self).__init__(*args, **kwargs)

        self.port = port

    def apply(self, component, *args, **kwargs):

        # iterate on all self port
        self_port = self.port
        for port_name in self_port:
            port = self_port[port_name]
            # bind it with its name
            component[port_name] = port

    def unapply(self, component, *args, **kwargs):

        # iterate on all self port
        self_port = self.port
        for port_name in self_port:
            # bind it with its name
            del component[port_name]


class SetIOCtl(C2CtlAnnotation):
    """Inject Binding controller in component implementation.
    """

    def get_value(self, component, *args, **kargs):

        return IOController.get_ctl(component)
