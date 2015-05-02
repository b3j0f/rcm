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
from b3j0f.rcm.binding.policy import (
    PolicyResultSet, Policy, ParameterizedPolicy,
    FirstPolicy, AllPolicy, CountPolicy, RandomPolicy,
    RoundAboutPolicy,
    SelectFirstPolicy, SelectAllPolicy, SelectCountPolicy,
    SelectRandomPolicy, SelectRoundaboutPolicy,
    AsyncPolicy, BestEffortPolicy,
    ResultFirstPolicy, ResultAllPolicy, ResultCountPolicy,
    ResultRandomPolicy, ResultRoundaboutPolicy
)


class TestPolicy(UTCase):
    """Test policy object.
    """

    pass


class TestParameterizedPolicy(TestPolicy):
    """Test ParameterizedPolicy.
    """

    def setUp(self):

        self.policy_cls = self._get_policy_cls()
        self.name = self._get_name()
        self.args, self.kwargs = self._get_args_kwargs()
        self.policy = self.policy_cls(
            name=self.name, *self.args, **self.kwargs
        )

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

    def _get_args_kwargs(self):
        """
        :return: initialization parameters.
        """
        return (), {}

    def test_noname(self):
        """Test to instantiate a parameterized policy without name.
        """

        self.assertRaises(TypeError, self.policy_cls)

    def test_name(self):
        """Test to instantiate a parameterized policy with a name.
        """

        self.assertEqual(self.name, self.policy.name)

    def test_none(self):
        """Test when param is None.
        """

        param = None

        result = self.policy(**{self.name: param})

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

        result = self.policy(**{self.name: param})

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

        result = self.policy(**{self.name: param})

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

        param = PolicyResultSet([i for i in range(50)])

        result = self.policy(**{self.name: param})

        self._assert_PolicyResultSet(param=param, result=result)

    def _assert_PolicyResultSet(self, param, result):
        """Specific assertion section of a policyresultset such as a parameter.

        :param PolicyResultSet param: input param policyresultset.
        :param result: policy result.
        """

        self.assertEqual(param, result)


class TestFirstPolicy(TestParameterizedPolicy):
    """Test First policy class.
    """

    def _get_policy_cls(self):

        return FirstPolicy


if __name__ == '__main__':
    main()
