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

__all__ = [
    'PolicyExecutor', 'PolicyResultSet'
]

from re import compile as re_compile


class PolicyResultSet(tuple):
    """In charge of embed a multiple policy result.
    """


class PolicyExecutor(object):
    """Manage execution of proxy policies.
    """

    POLICIES = 'policies'  #: policies attribute name

    __slots__ = [POLICIES]

    def __init__(self, policies=None):
        """
        :param policies: in case of not multiple port, a policies
            chooses at runtime which proxy method to run. If it is a dict, keys
            are method names and values are callable policies. Every
            policies takes in parameters:
            - port: self port,
            - resources: self resources,
            - proxies: list of proxies to execute,
            - name: the called method name,
            - instance: the proxy instance,
            - args: method args,
            - kwargs: method kwargs.
        :type policies: dict of callable by routine regex name or callable
        """

        super(PolicyExecutor, self).__init__()

        self.policies = self._init_policies(policies)

    def _init_policies(self, policies):
        """Init policies.

        :param policies:policy names or set of policy names by routine regex
            names.
        :type policies: str(s) or dict
        :rtype: dict
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

    def execute(
            self, port, proxies, routine, instance, args, kwargs, rname=None
    ):
        """Execute policies on input proxies related to additional parameters.

        :param str rname: routine name.
        :return: proxies to execute after policy execution.
        :rtype: list
        """

        policies = [
            self.policies[routinere] for routinere in self.policies
            if routinere.match('' if rname is None else rname)
        ]

        result = proxies

        for policy in policies:
            result = policy(proxies=result, *args, **kwargs)

        return result
