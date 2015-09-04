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

__all__ = ['IntentController', 'Intent']

from b3j0f.aop import weave
from b3j0f.rcm.ctl.core import Controller
from b3j0f.rcm.ctl.annotation import C2CtlAnnotation

from re import compile as re_compile

from inspect import getmembers


class IntentController(Controller):
    """Component intent controller. Manages interception of component interface
    calls.
    """

    class _IntentMatching(object):
        """
        Dedicated to manage intent matching.
        Matching condition is a regex on interface_name, callee_name \
        and dynamic_matching execution.
        """

        def __init__(
            self,
            interface_name=None,
            callee_name=None,
            dynamic_matching=None
        ):

            self.interface_name = \
                compile(interface_name) if interface_name is not None \
                else None
            self.callee_name = \
                compile(callee_name) if callee_name is not None \
                else None
            self.dynamic_matching = dynamic_matching

        def matches(self, interface_call):
            """
            Check if interface_name and callee_name and dynamic_matching \
            match with input interface_call.
            """

            result = False

            if self.interface_name is not None:
                result = self.interface_name.match(
                    interface_call.interface_name)
                if not result:
                    return result

            if self.callee_name is not None:
                result = self.callee_name.match(interface_call.callee_name)
                if not result:
                    return result

            if self.condition is not None:
                result = self.condition(interface_call)

            return result

    def add_intents(
        self,
        intents,
        target_name=None,
        member_name=None,
        dynamic_matching=None
    ):
        """
        Add an intent with optional arguments.
        The intent will intercepts if:
        * input interface_name matches with called interface name,
        * input callee_name matches with called callee name,
        * input dynamic_matching matches the interface_call.
        """

        splitter_target_name = target_name.split('.')
        port_name = splitter_target_name[0]
        if len(splitter_target_name) > 1:
            member_name = splitter_target_name[1]
        else:
            member_name = '*'

        port_regex = re_compile(port_name)
        member_regex = re_compile(member_name)

        for component in self._bound_to:
            ports = component.get_ports(
                select=lambda name, port: port_regex.matches(name)
            )
            for port in ports:
                for name, member in getmembers(
                    port, lambda m: member_regex.matches(
                        getattr(m, '__name__', '')
                    )
                ):
                    weave(member, advices=intents, ctx=port)

    def remove_intent(self, intent):
        """
        Remove an intent.
        """

        del self.matchings_per_intent[intent]

    def get_intent(self, interface_call):
        """
        """

        result = []
        for intent, matching in enumerate(self.matchings_per_intent):
            if matching.match(interface_call):
                result.append(intent)

        return result


class Intent(C2CtlAnnotation):
    """Inject an IntentController into a component implementation.
    """

    def get_value(self, component, *args, **kwargs):

        return IntentController.get_ctl(component)
