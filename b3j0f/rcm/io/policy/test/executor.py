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
from b3j0f.rcm.io.policy.executor import PolicyExecutor, PolicyResultSet
from random import randint


class TestPolicyResultSet(UTCase):
    """Test the PolicyResultSet.
    """

    def __init__(self, *args, **kwargs):

        super(TestPolicyResultSet, self).__init__(*args, **kwargs)

    def test_empty(self):
        """Test an empty policy result set.
        """

        prs = PolicyResultSet()

        self.assertFalse(prs)

    def test_one_elt(self):
        """Test a policy result set with one element.
        """

        policy = lambda *args, **kwargs: None
        prs = PolicyResultSet([policy])

        self.assertEqual(len(prs), 1)

    def test_many_elt(self):
        """Test a policy result set with several
        """

        count = randint(5, 10)
        prs = PolicyResultSet(
            [lambda *args, **kwargs: None for _ in range(count)]
        )

        self.assertEqual(len(prs), count)


class TestPolicyExecutor(UTCase):
    """Test PolicyExecutor class.
    """

    def _policy(self, rname, *args, **kwargs):
        """Policy which increments the rname
        """
        self.count.setdefault(rname, 0)
        self.count[rname] += 1

    def setUp(self):

        super(TestPolicyExecutor, self).setUp()

        self.count = {}  # dict of count by rname
        self.pex = PolicyExecutor()

    def test_empty(self):
        """Test without policy.
        """
        result = self.pex.execute(proxies=None)

        self.assertFalse(result)

    def test_global_policy(self):
        """Test one global policy.
        """
        self.pex.policies = {None: [self._policy]}

        self.pex.execute(proxies=None, rname='test')

        self.assertEqual(self.count, {'test': 1})

        self.pex.execute(proxies=None)

        self.assertEqual(self.count, {'test': 1, None: 1})

    def test_spe_policy(self):
        """Test with one specific policy.
        """
        self.pex.policies = {'test': [self._policy]}

        self.pex.execute(proxies=None, rname='')

        self.assertFalse(self.count)

        self.pex.execute(proxies=None, rname='test')

        self.assertEqual(self.count, {'test': 1})

    def test_re_policy(self):
        """Test with one regex policy
        """

        self.pex.policies = {'^test': [self._policy]}

        self.pex.execute(proxies=None, rname='')

        self.assertFalse(self.count)

        self.pex.execute(proxies=None, rname='test')

        self.assertEqual(self.count, {'test': 1})

    def test_policies(self):
        """Test three global, specific and regex policies.
        """

        self.pex.policies = {
            None: [self._policy],
            'test': [self._policy],
            '^test.?': [self._policy]
        }

        self.pex.execute(proxies=None)

        self.assertEqual(self.count, {None: 1})

        self.pex.execute(proxies=None, rname='test')

        self.assertEqual(self.count, {None: 1, 'test': 3})

        self.pex.execute(proxies=None, rname='testi')

        self.assertEqual(self.count, {None: 1, 'test': 3, 'testi': 2})

if __name__ == '__main__':
    main()
