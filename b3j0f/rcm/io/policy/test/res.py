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

"""Test
"""

from unittest import main

from b3j0f.rcm.io.policy.res import (
    ResultFirstPolicy, ResultAllPolicy, ResultCountPolicy,
    ResultRandomPolicy, ResultRoundaboutPolicy
)
from b3j0f.rcm.io.policy.test.sel import (
    TestFirstPolicy, TestAllPolicy, TestCountPolicy, TestRandomPolicy,
    TestRoundaboutPolicy
)


class TestResultFirstPolicy(TestFirstPolicy):
    """Test ResultFirstPolicy.
    """
    def _get_policy_cls(self):

        return ResultFirstPolicy

    def _get_name(self):

        return None

    def _get_params(self, param):

        return {'results': param}


class TestResultAllPolicy(TestAllPolicy):
    """Test ResultAllPolicy.
    """
    def _get_policy_cls(self):

        return ResultAllPolicy

    def _get_name(self):

        return None

    def _get_params(self, param):

        return {'results': param}


class TestResultCountPolicy(TestCountPolicy):
    """Test ResultCountPolicy.
    """
    def _get_policy_cls(self):

        return ResultCountPolicy

    def _get_name(self):

        return None

    def _get_params(self, param):

        return {'results': param}


class TestResultRandomPolicy(TestRandomPolicy):
    """Test ResultRandomPolicy.
    """
    def _get_policy_cls(self):

        return ResultRandomPolicy

    def _get_name(self):

        return None

    def _get_params(self, param):

        return {'results': param}


class TestResultRoundaboutPolicy(TestRoundaboutPolicy):
    """Test ResultRoundaboutPolicy.
    """
    def _get_policy_cls(self):

        return ResultRoundaboutPolicy

    def _get_name(self):

        return None

    def _get_params(self, param):

        return {'results': param}


if __name__ == '__main__':
    main()
