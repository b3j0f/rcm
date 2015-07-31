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

"""This module provides proxy results policy classes.

A result selection is a function which takes in parameters:

- port: proxy port.
- resources: port resources.
- proxies: list of port proxies.
- name: method name being executed.
- args and kwargs: respectively method varargs and keywords,
- results: list of proxy execution results.

And returns one object or a PolicyResultSet.

- resall: select all proxy results.
- resfirst: select the first proxy result or an empty list of proxies.
- rescount: select (random) proxy result between [inf;sup].
- resrandom: select one random proxy result.
- resroundabout: select iteratively a proxy result among proxy results. The
    first call select the first proxy result. Second call, the second. When all
    proxy have been called once, the policy starts again with the first
    proxy result.
"""

__all__ = [
    'ResultFirstPolicy', 'ResultAllPolicy', 'ResultCountPolicy',
    'ResultRandomPolicy', 'ResultRoundaboutPolicy',
]

from b3j0f.rcm.io.policy.sel import (
    FirstPolicy, AllPolicy, CountPolicy, RandomPolicy, RoundaboutPolicy
)


class ResultFirstPolicy(FirstPolicy):
    """Apply first policy on results.
    """

    def __init__(self, *args, **kwargs):

        super(ResultFirstPolicy, self).__init__(
            name='results', *args, **kwargs
        )


class ResultAllPolicy(AllPolicy):
    """Apply all policy on results.
    """
    def __init__(self, *args, **kwargs):

        super(ResultAllPolicy, self).__init__(name='results', *args, **kwargs)


class ResultCountPolicy(CountPolicy):
    """Apply count policy on results.
    """
    def __init__(self, *args, **kwargs):

        super(ResultCountPolicy, self).__init__(
            name='results', *args, **kwargs
        )


class ResultRandomPolicy(RandomPolicy):
    """Apply random policy on results.
    """
    def __init__(self, *args, **kwargs):

        super(ResultRandomPolicy, self).__init__(
            name='results', *args, **kwargs
        )


class ResultRoundaboutPolicy(RoundaboutPolicy):
    """Apply roundabout policy on results.
    """
    def __init__(self, *args, **kwargs):

        super(ResultRoundaboutPolicy, self).__init__(
            name='results', *args, **kwargs
        )
