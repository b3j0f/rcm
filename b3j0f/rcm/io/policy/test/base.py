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

from b3j0f.utils.ut import UTCase
from b3j0f.rcm.io.policy.sel import (
    PolicyResultSet, Policy, ParameterizedPolicy,
    FirstPolicy, AllPolicy, CountPolicy, RandomPolicy,
    RoundaboutPolicy,
    SelectFirstPolicy, SelectAllPolicy, SelectCountPolicy,
    SelectRandomPolicy, SelectRoundaboutPolicy
)
from b3j0f.rcm.io.policy.test.core import TestParameterizedPolicy


class TestFirstPolicy(TestParameterizedPolicy):
    """Test First policy class.
    """

    def _get_policy_cls(self):

        return FirstPolicy

    def _assert_PolicyResultSet(self, param, result):

        self.assertEqual(result, param[0])

    def _assert_empty_PolicyResultSet(self, param, result):

        self.assertIsNone(result)


class TestAllPolicy(TestParameterizedPolicy):
    """Test AllPolicy.
    """
    def _get_policy_cls(self):

        return AllPolicy


class TestCountPolicy(TestParameterizedPolicy):
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
        param = PolicyResultSet()
        params = self._get_params(param)
        self.assertRaises(CountPolicy.CountError, policy, **params)


class TestRandomPolicy(TestParameterizedPolicy):
    """Test RandomPolicy.
    """
    def _get_policy_cls(self):

        return RandomPolicy

    def _assert_PolicyResultSet(self, param, result):

        self.assertIn(result, param)

    def _assert_empty_PolicyResultSet(self, param, result):

        self.assertIsNone(result)


class TestRoundaboutPolicy(TestParameterizedPolicy):
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


class TestSelectFirstPolicy(TestFirstPolicy):
    """Test SelectFirstPolicy.
    """
    def _get_policy_cls(self):

        return SelectFirstPolicy

    def _get_name(self):

        return None

    def _get_params(self, param):

        return {'proxies': param}


class TestSelectAllPolicy(TestAllPolicy):
    """Test SelectAllPolicy.
    """
    def _get_policy_cls(self):

        return SelectAllPolicy

    def _get_name(self):

        return None

    def _get_params(self, param):

        return {'proxies': param}


class TestSelectCountPolicy(TestCountPolicy):
    """Test SelectCountPolicy.
    """
    def _get_policy_cls(self):

        return SelectCountPolicy

    def _get_name(self):

        return None

    def _get_params(self, param):

        return {'proxies': param}


class TestSelectRandomPolicy(TestRandomPolicy):
    """Test SelectRandomPolicy.
    """
    def _get_policy_cls(self):

        return SelectRandomPolicy

    def _get_name(self):

        return None

    def _get_params(self, param):

        return {'proxies': param}


class TestSelectRoundaboutPolicy(TestRoundaboutPolicy):
    """Test SelectRoundaboutPolicy.
    """
    def _get_policy_cls(self):

        return SelectRoundaboutPolicy

    def _get_name(self):

        return None

    def _get_params(self, param):

        return {'proxies': param}


if __name__ == '__main__':
    main()
