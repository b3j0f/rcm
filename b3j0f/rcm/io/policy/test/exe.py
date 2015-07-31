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

from b3j0f.rcm.io.policy.exe import (
    AsyncPolicy, BestEffortPolicy, StatelessPolicy
)
from b3j0f.rcm.io.policy.test.sel import TestParameterizedPolicy


class TestAsyncPolicy(TestParameterizedPolicy):
    """Test AsyncPolicy.
    """

    def _get_policy_cls(self):

        return AsyncPolicy

    def _callback(self, *args, **kwargs):
        """
        Proxy execution callback.
        """

        self._callback_params = getattr(self, '_callback_params', [])

        self._callback_params.append((args, kwargs))

    def _get_name(self):

        return None

    def _get_args_kwargs(self):

        return (), {'callback': self._callback}

    def _get_params(self, param):

        return {'proxies': param, 'routine': '__str__'}

    def _test_not_policy_result(self, param, result):

        self.assertIsNone(result)

        self.policy.join()

        result = self._callback_params[0][1]['result']

        self.assertEqual(result, str(param))

    def _assert_empty_PolicyResultSet(self, param, result):

        self.assertIsNone(result)

        self.policy.join()

        self.assertFalse(hasattr(self, 'self._callback_params'))

    def _assert_PolicyResultSet(self, param, result):

        self.assertIsNone(result)

        self.policy.join()

        results = [
            self._callback_params[i][1]['result'] for i in range(self.count)
        ]

        self.assertEqual(list(map(lambda x: str(x), param)), results)

    def test_error(self):
        """Test when the async proxy execution raises and error.
        """

        def proxy():
            raise ValueError()

        self.policy(proxies=proxy, routine='__call__')

        self.policy.join()

        result = self._callback_params[0][1]['error']

        self.assertIsInstance(result, ValueError)


class TestAsyncPolicyWithoutCallback(TestParameterizedPolicy):
    """Test AsyncPolicy without callback.
    """

    def _get_policy_cls(self):

        return AsyncPolicy

    def _get_name(self):

        return None

    def _get_params(self, param):

        return {'proxies': param, 'routine': '__str__'}

    def _test_not_policy_result(self, param, result):

        self.assertIsNone(result)

        self.policy.join()

    def _assert_empty_PolicyResultSet(self, param, result):

        self.assertIsNone(result)

        self.policy.join()

    def _assert_PolicyResultSet(self, param, result):

        self.assertIsNone(result)

        self.policy.join()

    def test_error(self):
        """Test when the async proxy execution raises and error.
        """

        def proxy():
            """testing proxy.
            """
            raise ValueError()

        self.policy(proxies=proxy, routine='__call__')

        self.policy.join()


class TestBestEffortPolicy(TestParameterizedPolicy):
    """Test BestEffortPolicy.
    """

    def _get_policy_cls(self):

        return BestEffortPolicy

    def _get_name(self):

        return None

    def _get_args_kwargs(self):

        return (), {}

    def _get_params(self, param):

        return {'proxies': param, 'routine': '__str__'}

    def _test_not_policy_result(self, param, result):

        self.assertEqual(result, str(param))

    def _assert_empty_PolicyResultSet(self, param, result):

        self.assertIsNone(result)

    def _assert_PolicyResultSet(self, param, result):

        self.assertEqual(result, str(param[0]))

        class Proxy(object):
            """Test proxy.
            """
            def __call__(self):

                return self

        instance = Proxy()

        # check proxies without errors
        result = self.policy(
            instance=instance, routine='__call__'
        )
        self.assertIsNot(instance, result)


class TestStatelessPolicy(TestParameterizedPolicy):
    """Test StatelessPolicy.
    """

    def _get_policy_cls(self):

        return StatelessPolicy

    def _get_name(self):

        return None

    def _get_args_kwargs(self):

        return (), {}

    def _get_params(self, param):

        return {'proxies': param, 'routine': '__str__'}

    def _test_not_policy_result(self, param, result):

        self.assertEqual(result, str(param))

    def _assert_empty_PolicyResultSet(self, param, result):

        self.assertIsNone(result)

    def _assert_PolicyResultSet(self, param, result):

        self.assertEqual(result, str(param[0]))

        def proxy():
            """test proxy.
            """
            raise ValueError()

        # check proxies without errors
        proxies = [proxy, proxy, proxy]
        proxies = PolicyResultSet(proxies)
        result = self.policy(
            proxies=proxies, routine='__call__'
        )
        self.assertEqual(result, None)

        # check proxies with only one which is executable
        proxies = [proxy, proxy, proxy, lambda: 2]
        proxies = PolicyResultSet(proxies)
        result = self.policy(
            proxies=proxies, routine='__call__'
        )
        self.assertEqual(result, 2)

        # check proxies with maxtry less than valid proxy
        self.policy.maxtry = 2
        self.assertRaises(
            BestEffortPolicy.MaxTryError, self.policy,
            proxies=proxies, routine='__call__'
        )

        # check proxies with a timeout
        self.policy.maxtry = 4
        self.policy.timeout = 1
        self.assertRaises(
            BestEffortPolicy.TimeoutError, self.policy,
            proxies=proxies, routine='__call__'
        )


if __name__ == '__main__':
    main()
