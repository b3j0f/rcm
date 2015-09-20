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

"""selection porlicy UTs.
"""

from unittest import main

from random import randint

from b3j0f.utils.ut import UTCase
from b3j0f.rcm.io.policy.selection import (
    ProxySelection,
    FirstPolicy, AllPolicy, CountPolicy, RandomPolicy, RoundaboutPolicy
)


class TestProxySelection(UTCase):
    """Test the ProxySelection.
    """

    def __init__(self, *args, **kwargs):

        super(TestProxySelection, self).__init__(*args, **kwargs)

    def test_empty(self):
        """Test an empty policy result set.
        """

        prs = ProxySelection()

        self.assertFalse(prs)

    def test_one_elt(self):
        """Test a policy result set with one element.
        """

        policy = lambda *args, **kwargs: None
        prs = ProxySelection([policy])

        self.assertEqual(len(prs), 1)

    def test_many_elt(self):
        """Test a policy result set with several
        """

        count = randint(5, 10)
        prs = ProxySelection(
            [lambda *args, **kwargs: None for _ in range(count)]
        )

        self.assertEqual(len(prs), count)


class TestPolicy(UTCase):
    """Test policy object.
    """

    def setUp(self):

        super(TestPolicy, self).setUp()

        self.count = 50  # number of proxies to generate in a ProxySelection
        self.policy_cls = self._get_policy_cls()  # get policy cls
        self.policy = self._get_policy()  # get policy

    def _get_policy_cls(self):
        """
        :return: parameterized policy class.
        """

        raise NotImplementedError()

    def _get_policy(self):
        """Instantiate a new policy related to self name and args/kwargs.
        """

        self.args, self.kwargs = self._get_args_kwargs()

        result = self.policy_cls(
            *self.args, **self.kwargs
        )
        return result

    def _get_args_kwargs(self):
        """
        :return: initialization parameters.
        """
        return (), {}

    def _get_params(self, param):
        """
        :return: policy invocation params.
        :rtype: dict
        """

        return {'proxies': param}

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
        """Assert a not ProxySelection result.

        :param (not ProxySelection) param:
        """

        self.assertEqual(result, param)

    def test_empty_PolicyResultSet(self):
        """Test when param is an empty policy result set.
        """

        param = ProxySelection()

        params = self._get_params(param)
        result = self.policy(**params)

        self._assert_empty_PolicyResultSet(param=param, result=result)

    def _assert_empty_PolicyResultSet(self, param, result):
        """Specific assertion section of an empty policyresultset such as a
        parameter.

        :param ProxySelection param: empty policyresultset.
        :param result: policy result.
        """

        self.assertEqual(param, result)

    def test_PolicyResultSet(self):
        """Test when param is a policy result set.
        """

        param = ProxySelection([i for i in range(self.count)])

        params = self._get_params(param)
        result = self.policy(**params)

        self._assert_PolicyResultSet(param=param, result=result)

    def _assert_PolicyResultSet(self, param, result):
        """Specific assertion section of a policyresultset such as a parameter.

        :param ProxySelection param: input param policyresultset.
        :param result: policy result.
        """

        self.assertEqual(param, result)


class TestFirstPolicy(TestPolicy):
    """Test First policy class.
    """

    def _get_policy_cls(self):

        return FirstPolicy

    def _assert_PolicyResultSet(self, param, result):

        self.assertEqual(result, param[0])

    def _assert_empty_PolicyResultSet(self, param, result):

        self.assertIsNone(result)


class TestAllPolicy(TestPolicy):
    """Test AllPolicy.
    """
    def _get_policy_cls(self):

        return AllPolicy


class TestCountPolicy(TestPolicy):
    """Test CountPolicy.
    """

    def _get_policy_cls(self):

        return CountPolicy

    def _get_args_kwargs(self):

        self.random = not getattr(self, 'random', True)

        self.inf = 0
        self.sup = int(self.count / 2)

        return (), {'inf': self.inf, 'sup': self.sup, 'random': self.random}

    def _assert_PolicyResultSet(self, param, result):

        final_result = set(result) & set(param)
        self.assertEqual(len(final_result), self.sup)

        self.policy = self._get_policy()

        if self.random:  # call one more time the same test with random True
            self.test_PolicyResultSet()

    def _assert_empty_PolicyResultSet(self, param, result):

        self.assertFalse(result)

    def test_error(self):
        """Test to raise an error if proxies count is lower than inf limit.
        """

        policy = self._get_policy()
        policy.inf = 5
        param = ProxySelection()
        params = self._get_params(param)
        self.assertRaises(CountPolicy.CountError, policy, **params)


class TestRandomPolicy(TestPolicy):
    """Test RandomPolicy.
    """
    def _get_policy_cls(self):

        return RandomPolicy

    def _assert_PolicyResultSet(self, param, result):

        self.assertIn(result, param)

    def _assert_empty_PolicyResultSet(self, param, result):

        self.assertIsNone(result)


class TestRoundaboutPolicy(TestPolicy):
    """Test RoundaboutPolicy.
    """
    def _get_policy_cls(self):

        return RoundaboutPolicy

    def _assert_empty_PolicyResultSet(self, param, result):

        self.assertIsNone(result)

    def _assert_PolicyResultSet(self, param, result):

        self.assertEqual(result, param[0])

        self.index = getattr(self, 'index', 0)

        for index in range(1, self.count):
            params = self._get_params(param)
            result = self.policy(**params)
            self.assertEqual(result, param[index])
        else:
            params = self._get_params(param)
            result = self.policy(**params)
            self.assertEqual(result, param[0])

if __name__ == '__main__':
    main()
