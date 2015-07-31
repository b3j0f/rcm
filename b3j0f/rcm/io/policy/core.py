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

"""This module provides policy helper classes and policy result set for
application in a port proxy.
"""

__all__ = ['PolicyResultSet', 'Policy', 'ParameterizedPolicy']

from collections import Callable


class PolicyResultSet(tuple):
    """In charge of embed a multiple policy result.
    """


class Policy(object):
    """In charge of applying a policy on proxy selection/execution/results.
    """

    def __call__(self, *args, **kwargs):

        raise NotImplementedError()


class ParameterizedPolicy(Policy):
    """In charge of applying a policy on a specific policy parameter designed
    by this ``name`` attribute.

    Choose the parameter by default.
    """
    def __init__(self, name, *args, **kwargs):
        """
        :param str name: parameter name.
        """

        super(ParameterizedPolicy, self).__init__(*args, **kwargs)

        self.name = name

    def __call__(self, *args, **kwargs):
        """
        :return: kwargs[self.name]
        """

        result = kwargs[self.name]

        return result


class PolicyRules(object):
    """Manage three policies of proxy selection, execution and result.
    """

    SELECT_POLICY = 'selectp'  #: selection policy attribute name
    EXEC_POLICY = 'execp'  #: execution policy attribute name
    RESULT_POLICY = 'resultp'  #: result policy attribute name

    __slots__ = [SELECT_POLICY, EXEC_POLICY, RESULT_POLICY]

    class PolicyRulesType(dict):

        def apply(self, policies, rname=None):

            raise NotImplementedError()

        def unapply(self, policies, rname=None):

            raise NotImplementedError()

        def __iadd__(self, value):

            self.apply(value)

        def __isub__(self, value):

            self.unapply(value)

        def __getitem__(self, key):

            return self.get(rname=key)

        def get(self, rname=None):
            """Get the right policy rule related to specific policy and
            routine name.

            :param str rname: routine name.
            :return: policy rule.
            """

            result = None

            # if policy is a set of rules by routine name
            if isinstance(policy, dict):
                result = policy.get(rname)
            # if policy is a rule
            elif isinstance(policy, Callable):
                result = policy

            return result

    def __init__(self, selectp=None, execp=None, resultp=None):
        """
        :param selectp: in case of not multiple port, a selectp
            chooses at runtime which proxy method to run. If it is a dict, keys
            are method names and values are callable selectp. Every
            selectp takes in parameters:
            - port: self port,
            - resources: self resources,
            - proxies: list of proxies to execute,
            - name: the called method name,
            - instance: the proxy instance,
            - args: method args,
            - kwargs: method kwargs.
        :type selectp: dict or callable
        :param execp: in case of not multiple port, a execp chooses at
            runtime how to execute a proxy method. If it is a dict, keys are
            method names and values are callable execp. Every execp
            takes in parameters:
            - port: self port,
            - resources: self resources,
            - proxies: list of proxies to execute,
            - name: the called method name,
            - instance: the proxy instance,
            - args: method args,
            - kwargs: method kwargs.
        :type execp: dict or callable
        :param resultp: in case of not multiple port, a resultp
            choose at which proxy method result to return. If it is a dict,
            keys are method names and values are callable resultp. Every
            resultp takes in parameters:
            - port: self port,
            - resources: self resources,
            - proxies: list of proxies to execute,
            - name: the called method name,
            - instance: the proxy instance,
            - args: method args,
            - kwargs: method kwargs,
            - results: method results.
        :type resultp: dict or callable
        """

        self.selectp = selectp
        self.execp = execp
        self.resultp = resultp

    @staticmethod
    def _rule(policy, rname=None):
        """Get the right policy rule related to specific policy and
        routine name.

        :param policy: policy to use.
        :type policy: dict or Callable
        :param str rname: routine name.
        :return: policy rule.
        """

        result = None

        # if policy is a set of rules by routine name
        if isinstance(policy, dict):
            result = policy.get(rname)
        # if policy is a rule
        elif isinstance(policy, Callable):
            result = policy

        return result

    def selectpr(self, rname=None):
        """Get the right selection policy rule related to a routine name.

        :param str rname: routine name.
        :return: selection policy rule.
        """

        return self._rule(policy=self.selectp, rname=rname)

    def execpr(self, rname=None):
        """Get the right execution policy rule related to a routine name.

        :param str rname: routine name.
        :return: execution policy rule.
        """

        return self._rule(policy=self.execp, rname=rname)

    def resultpr(self, rname=None):
        """Get the right result policy rule related to a routine name.

        :param str rname: routine name.
        :return: policy rule.
        """

        return self._rule(policy=self.resultp, rname=rname)

    def apply_policies(ptype, *policies):
        """Apply policies in the input policy_rules.

        :param PolicyRules policyrules: policyrules to update.
        :param list policies: list of policies to apply.
        """

        raise NotImplementedError()

    def unapply_policies(ptype, *policies):
        """Unapply policies from the input policy_rules.

        :param ptype: policy type to unapply.
        :param list policies: list of policies to apply.
        """

        raise NotImplementedError()
