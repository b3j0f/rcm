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

__all__ = ['PolicySet']

from re import compile as re_compile

from functools import reduce

from operator import add

from copy import deepcopy

from b3j0f.aop import weave
from b3j0f.rcm.io.proxy import ProxySet


class PolicySet(object):
    """Set of selection/execution proxy policies.
    """

    #: routine name regex
    ROUTINE_REGEX = re_compile('^[A-Za-z_][0-9A-Za-z_]*')

    #: proxy selection policies attribute name
    SEL_POLICIES = '_sel_policies'
    #: proxy selection policies specific attribute name
    _SEL_SPE_POLICIES = '_sel_spe_policies'
    #: proxy selection policies regex attribute name
    _SEL_REG_POLICIES = '_sel_reg_policies'
    #: proxy selection policies by routine name attribute name
    _SEL_POLICIES_BY_RNAME = '_sel_policies_by_rname'
    #: proxy execution policies attribute name
    EXE_POLICIES = '_exe_policies'
    #: proxy execution policies specific attribute name
    _EXE_SPE_POLICIES = '_exe_spe_policies'
    #: proxy execution policies regex attribute name
    _EXE_REG_POLICIES = '_exe_reg_policies'
    #: proxy execution policies by routine name attribute name
    _EXE_POLICIES_BY_RNAME = '_exe_policies_by_rname'

    _SELECTION_KIND = 'sel'  #: selection policy kind
    _EXECUTION_KIND = 'exe'  #: execution policy kind

    __slots__ = [
        SEL_POLICIES,
        _SEL_REG_POLICIES, _SEL_SPE_POLICIES, _SEL_POLICIES_BY_RNAME,
        EXE_POLICIES,
        _EXE_REG_POLICIES, _EXE_SPE_POLICIES, _EXE_POLICIES_BY_RNAME
    ]

    def __init__(self, sel_policies=None, exe_policies=None):
        """
        :param dict sel_policies: dict of proxy selection policies by routine
            (regex) name. If the routine name is None, related policies are
            applied on all proxy routines.
            A policy is a function which takes in parameters:
            - port: self port,
            - resources: self resources,
            - proxies: list of proxies to execute,
            - name: the called method name,
            - instance: the proxy instance,
            - args: method args,
            - kwargs: method kwargs.
        :param dict exe_policies: dict of proxy execution policies by routine
            (regex) name. If the routine name is None, related policies are
            applied on all proxy routines.
            A policy is an advice (see also b3j0f.aop.advice) which takes in
            parameter a joinpointexecution.
        """

        super(PolicySet, self).__init__()

        # init protected attributes
        self._sel_policies = {}
        self._sel_spe_policies = {}
        self._sel_reg_policies = {}
        self._sel_policies_by_rname = {}
        self._exe_policies = {}
        self._exe_spe_policies = {}
        self._exe_reg_policies = {}
        self._exe_policies_by_rname = {}

        # init policies
        self.sel_policies = sel_policies
        self.exe_policies = exe_policies

    @property
    def sel_policies(self):
        """Get proxy selection policies.

        :rtype: dict
        """

        return self._sel_policies

    @sel_policies.setter
    def sel_policies(self, sel_policies):
        """Change of proxy selection policies.

        :param dict sel_policies: new policies to use.
        """

        self._set_policies(sel_policies, self._SELECTION_KIND)

    @property
    def exe_policies(self):
        """Get proxy execution policies.

        :rtype: dict
        """

        return self._exe_policies

    @exe_policies.setter
    def exe_policies(self, exe_policies):
        """Change of proxy execution policies.

        :param dict exe_policies: new policies to use.
        """

        self._set_policies(exe_policies, self._EXECUTION_KIND)

    def _set_policies(self, policies, kind):
        """Fill this policy attributes.

        :param dict policies: policies from where get policies to use.
        :param dict selfpolicies: public self policies attribute.
        :param dict spe: specific policies to fill.
        :param dict reg: regex policies to fill.
        :param dict by_rname: policies by routine name to empty.
        """

        selfpolicies = getattr(self, '_{0}_policies'.format(kind))
        spe = getattr(self, '_{0}_spe_policies'.format(kind))
        reg = getattr(self, '_{0}_reg_policies'.format(kind))
        by_rname = getattr(self, '_{0}_policies_by_rname'.format(kind))

        # init self policies
        selfpolicies.clear()
        if policies is not None:
            policies.update(deepcopy(policies))

        spe.clear()  # clear specific policies
        reg.clear()  # clear regex policies
        by_rname.clear()  # clear self policies by rname

        for rname in selfpolicies:  # fill specific and regex policies
            # is specific routine name ?
            if rname is None or PolicySet.ROUTINE_REGEX.match(rname):
                spe[rname] = list(selfpolicies[rname])

            else:  # otherwise, this is a regex routine name
                re_rname = re_compile(rname)
                reg[re_rname] = list(selfpolicies[rname])

    @staticmethod
    def _get_policies(spe, reg, by_rname, rname=None):
        """Get policies corresponding to input routine name.

        :param str rname: routine name.
        :param dict spe:
        :param dict reg:
        :param dict by_rname:
        :return: policies  to execute after policy execution.
        :rtype: list
        """

        result = None

        if rname in by_rname:  # check if policies are in memory
            result = by_rname[rname]

        else:  # identify policies able to process the rname
            result = []

            if None in spe:  # apply global policies
                result += spe[None]

            # apply specific policies
            if rname is not None and rname in spe:
                result += spe[rname]

            if reg:  # if regex policies is not empty
                result += reduce(
                    add,
                    [  # apply regex policies
                        reg[routinere] for routinere in reg
                        if routinere.match('' if rname is None else rname)
                    ]
                )

            by_rname[rname] = result  # save policies in memory

        return result

    def selectproxies(self, proxies, rname=None, *args, **kwargs):
        """Select proxies related to this policies.

        The selection is done in executing sequentially policies with proxies
        in parameters. Each iteration uses the previous policy selection.

        :param str rname: routine name.
        :return: proxies to execute after policy execution.
        :rtype: list
        """

        policies = self._get_policies(
            spe=self._sel_spe_policies, reg=self._sel_reg_policies,
            by_rname=self._sel_policies_by_rname
        )

        result = proxies

        for policy in policies:  # execute found policies on proxies
            result = policy(proxies=result, rname=rname, *args, **kwargs)

        return result

    def executeproxies(self, proxies, rname=None, *args, **kwargs):
        """Execute proxies related to this policies.

        The execution is done in weaving advices on proxies.

        :param proxies: proxies whete weave advices to.
        :param str rname: routine name.
        """

        # get proxy execution policies
        policies = self._get_policies(
            spe=self._exe_spe_policies, reg=self._exe_reg_policies,
            by_rname=self._exe_policies_by_rname
        )

        # ensure proxies are many
        _proxies = proxies
        if not isinstance(proxies, ProxySet):
            _proxies = [proxies]

        for proxy in _proxies:  # weave policies on all proxies
            weave(target=proxy, advices=policies)
