#!/usr/bin/env python
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

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.rcm.io.policy.core import (
    PolicyRules, Policy, ParameterizedPolicy, PolicyResultSet
)


class TestPolicy(UTCase):
    """Test policy object.
    """

    def _get_policy_cls(self):
        """
        :return: parameterized policy class.
        """
        return Policy


class TestParameterizedPolicy(TestPolicy):
    """Test ParameterizedPolicy.
    """

    def setUp(self, *args, **kwargs):

        super(TestParameterizedPolicy, self).setUp(*args, **kwargs)

        self.count = 50  # number of proxies to generate in a PolicyResultSet
        self.policy_cls = self._get_policy_cls()  # get policy cls
        self.policy = self._get_policy()  # get policy

    def _get_policy_cls(self):
        """
        :return: parameterized policy class.
        """
        return ParameterizedPolicy

    def _get_name(self):
        """
        :return: parameterized policy name.
        """

        return 'test'

    def _get_policy(self):
        """Instantiate a new policy related to self name and args/kwargs.
        """
        self.name = self._get_name()
        self.args, self.kwargs = self._get_args_kwargs()
        if self.name is not None:
            self.kwargs['name'] = self.name
        result = self.policy_cls(
            *self.args, **self.kwargs
        )
        return result

    def _get_args_kwargs(self):
        """
        :return: initialization parameters.
        """
        return (), {}

    def test_noname(self):
        """Test to instantiate a parameterized policy without name.
        """

        if self.name is not None:
            self.assertRaises(TypeError, self.policy_cls)

    def test_name(self):
        """Test to instantiate a parameterized policy with a name.
        """

        if self.name is not None:
            self.assertEqual(self.name, self.policy.name)

    def _get_params(self, param):
        """
        :return: policy invocation params.
        :rtype: dict
        """

        return {} if self.name is None else {self.name: param}

    def test_none(self):
        """Test when param is None.
        """

        param = None

        params = self._get_params(param)
        result = self.policy(**params)

        self._assert_none(result=result)

    def _assert_none(self, result):
        """Assert a none result.

        :param result: none result.
        """

        self.assertIsNone(result)

    def test_not_policyresultset(self):
        """Test to apply a policy on a not policyresultset.
        """

        param = []

        params = self._get_params(param)

        result = self.policy(**params)

        self._test_not_policy_result(param=param, result=result)

    def _test_not_policy_result(self, param, result):
        """Assert a not PolicyResultSet result.

        :param (not PolicyResultSet) param:
        """

        self.assertEqual(result, param)

    def test_empty_PolicyResultSet(self):
        """Test when param is an empty policy result set.
        """

        param = PolicyResultSet()

        params = self._get_params(param)
        result = self.policy(**params)

        self._assert_empty_PolicyResultSet(param=param, result=result)

    def _assert_empty_PolicyResultSet(self, param, result):
        """Specific assertion section of an empty policyresultset such as a
        parameter.

        :param PolicyResultSet param: empty policyresultset.
        :param result: policy result.
        """

        self.assertEqual(param, result)

    def test_PolicyResultSet(self):
        """Test when param is a policy result set.
        """

        param = PolicyResultSet([i for i in range(self.count)])

        params = self._get_params(param)
        result = self.policy(**params)

        self._assert_PolicyResultSet(param=param, result=result)

    def _assert_PolicyResultSet(self, param, result):
        """Specific assertion section of a policyresultset such as a parameter.

        :param PolicyResultSet param: input param policyresultset.
        :param result: policy result.
        """

        self.assertEqual(param, result)


class TestPolicyRules(UTCase):
    """Test PolicyRules class.
    """

    def setUp(self):

        super(TestPolicyRules, self).setUp()

        def execpr():
            """Execution policy rule.
            """

        def selectpr():
            """Selection policy rule.
            """

        def resultpr():
            """Result policy rule.
            """

        self.prs = PolicyRules(
            selectp=selectpr, execp=execpr, resultp=resultpr
        )

    def _assertpr(self, prname, rname=None):
        """Assert PolicyRules pr method.

        :param str prname: pr method name.
        """

        prmethod = getattr(self.prs, prname)

        prule = prmethod(rname=rname)

        self.assertTrue(prule.__name__, prname)

    def test_selectpr(self):
        """Test PolicyRules.selectpr method.
        """

        self._assertpr('selectpr')

    def test_execpr(self):
        """Test PolicyRules.execpr method.
        """

        self._assertpr('execpr')

    def test_resultpr(self):
        """Test PolicyRules.resultpr method.
        """

        self._assertpr('resultpr')

    def _assertprrname(self, prname):
        """Assert pr with specific rname.
        """

        rname = 'test'
        setattr(self.prs, prname[:-1], {rname: getattr(self.prs, prname)})
        self._assertpr(prname, rname=rname)

    def test_selectprrname(self):
        """Test PolicyRules.selectpr method with rname.
        """

        self._assertprrname('selectpr')

    def test_execprrname(self):
        """Test PolicyRules.execpr method with rname.
        """

        self._assertprrname('execpr')

    def test_resultprrname(self):
        """Test PolicyRules.resultpr method.
        """

        self._assertprrname('resultpr')


if __name__ == '__main__':
    main()
