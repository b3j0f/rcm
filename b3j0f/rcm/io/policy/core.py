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

from re import compile as re_compile


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
        :type selectp: dict of callable by routine regex name or callable
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
        :type execp: dict of callable by routine regex name or callable
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
        :type resultp: dict of callable by routine regex name or callable
        """

        self.selectp = self._init_policies(selectp)
        self.execp = self._init_policies(execp)
        self.resultp = self._init_policies(resultp)

    def _init_policies(self, policies):
        """Init policies.

        :param policies:policy names or set of policy names by routine regex
            names.
        :type policies: str(s) or dict
        """

        result = {}

        if policies is not None:
            if callable(policies):
                # default policies applyed on all routines
                policies = {'.*': policies}

            for routinere in policies:
                # compile routinere
                policy = policies[routinere]
                regex = re_compile(routinere)
                # append policy to the result
                result.setdefault(regex, []).append(policy)

        return result

    @staticmethod
    def _rule(policies, rname=None):
        """Get the right policy rules related to specific policies kind (and
        routine regex name).

        :param dict policies: policy rules to use.
        :param str rname: routine regex name.
        :return: policy execution function.
        """

        policies = [
            policies[routinere] for routinere in policies
            if routinere.match('' if rname is None else rname)
        ]

        def runpolicies(proxies, *args, **kwargs):
            """Run all policies on input parameters and returns proxies to run.
            """

            result = proxies

            for policy in policies:
                result = policy(proxies=result, *args, **kwargs)

            return result

        result = runpolicies

        return result

    def selectpr(self, rname=None):
        """Get the right selection policy rule related to a routine name.

        :param str rname: routine name.
        :return: selection policy rule.
        """

        return self._rule(policies=self.selectp, rname=rname)

    def execpr(self, rname=None):
        """Get the right execution policy rule related to a routine name.

        :param str rname: routine name.
        :return: execution policy rule.
        """

        return self._rule(policies=self.execp, rname=rname)

    def resultpr(self, rname=None):
        """Get the right result policy rule related to a routine name.

        :param str rname: routine name.
        :return: policy rule.
        """

        return self._rule(policies=self.resultp, rname=rname)
