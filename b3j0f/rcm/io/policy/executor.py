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

__all__ = ['PolicyExecutor', 'PolicyResultSet']

from re import compile as re_compile

from functools import reduce


class PolicyResultSet(tuple):
    """In charge of embed a multiple policy result.
    """


class PolicyExecutor(object):
    """Manage execution of proxy policies.
    """

    POLICIES = '_policies'  #: policies attr name
    _SPE_POLICIES = '_spe_policies'  #: specific policies attribute name
    _RE_POLICIES = '_re_policies'  #: re policies attr name
    _POLICIES_BY_RNAME = '_policies_by_rname'  #: policies by rname attr name

    __slots__ = [POLICIES, _RE_POLICIES, _SPE_POLICIES, _POLICIES_BY_RNAME]

    def __init__(self, policies=None):
        """
        :param dict policies: dict of callable policies by routine (regex) name
            . If the routine name is None, related policies are applied on all
            proxy routines.
            A policy takes in parameters:
            - port: self port,
            - resources: self resources,
            - proxies: list of proxies to execute,
            - name: the called method name,
            - instance: the proxy instance,
            - args: method args,
            - kwargs: method kwargs.
        """

        super(PolicyExecutor, self).__init__()

        # init protected attributes
        self._policies = self._spe_policies = self._re_policies = None
        self._policies_by_rname = {}
        # init policies
        self.policies = policies

    @property
    def policies(self):
        """Get policies.

        :rtype: dict
        """

        return self._policies

    @policies.setter
    def policies(self, policies):
        """Change of policies.

        :param dict policies: new policies to use.
        """
        # init self policies
        self._policies = {} if policies is None else policies.copy()

        self._spe_policies = {}  # init specific policies

        self._re_policies = {}  # init self re_policies

        self._policies_by_rname.clear()  # init self policies by rname

        routine_re = '^[A-Za-z_][0-9A-Za-z_]*'  # get routine name regex
        routine_re = re_compile(routine_re)

        for rname in self._policies:  # fill self policies and _re_policies
            if rname is None or routine_re.match(rname):
                self._spe_policies[rname] = list(policies[rname])

            else:
                self._re_policies[re_compile(rname)] = list(policies[rname])

    def execute(self, proxies, rname=None, *args, **kwargs):
        """Execute policies on input proxies related to additional parameters.

        :param str rname: routine name.
        :return: proxies to execute after policy execution.
        :rtype: list
        """

        if rname in self._policies_by_rname:  # check if policies are in memory
            policies = self._policies_by_rname[rname]

        else:  # identify policies able to process the rname
            policies = []

            if None in self._spe_policies:  # apply global policies
                policies += self._spe_policies[None]

            # apply specific policies
            if rname is not None and rname in self._spe_policies:
                policies += self._spe_policies[rname]

            policies += reduce(
                lambda x, y: x + y,
                [  # apply regex policies
                    self._re_policies[routinere]
                    for routinere in self._re_policies
                    if routinere.match('' if rname is None else rname)
                ],
                []
            )

            self._policies_by_rname[rname] = policies  # save policies in mem

        result = proxies

        for policy in policies:  # execute found policies on proxies
            result = policy(proxies=result, rname=rname, *args, **kwargs)

        return result
