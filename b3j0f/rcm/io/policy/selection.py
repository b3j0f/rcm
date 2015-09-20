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

"""This module provides proxy selection policy classes.

A policy is a callable which takes in parameters:

- port: proxy port.
- resources: port resources.
- proxies: list of port proxies.
- name: method name being executed.
- args and kwargs: respectively method varargs and keywords.

And returns one proxy or a ProxySelection.

Here are types of selection proxies classes:

- SelectionPolicy: abstract class provided in order to make easier the
    implementation of selection policies.
- AllPolicy: select all proxies.
- FirstPolicy: select the first proxy or an empty list of proxies.
- CountPolicy: select (random) proxies between [inf;sup].
- RandomPolicy: select one random proxy.
- RoundaboutPolicy: select iteratively a proxy among proxies. The first
    call select the first proxy. Second call, the second. When all
    proxies have been called once, the policy starts again with the first
    proxy.
"""

__all__ = [
    'ProxySelection', 'SelectionPolicy',
    'FirstPolicy', 'AllPolicy', 'CountPolicy', 'RandomPolicy',
    'RoundaboutPolicy'
]

from random import shuffle, choice

from sys import maxsize


class ProxySelection(tuple):
    """Set of selected proxies from proxy selection policies.
    """


class SelectionPolicy(object):
    """In charge of applying a policy on proxy selection.
    """

    def __call__(self, proxies, *args, **kwargs):
        """
        Apply self selection policy on input proxies.

        :return: proxies to execute (``proxies`` by default).
        """

        return proxies


class FirstPolicy(SelectionPolicy):
    """Choose first value in specific parameter if parameter is
    ProxySelection, otherwise, return parameter.
    """

    def __call__(self, *args, **kwargs):

        result = super(FirstPolicy, self).__call__(*args, **kwargs)

        if isinstance(result, ProxySelection):
            result = result[0] if result else None

        return result


class AllPolicy(SelectionPolicy):
    """Select all policies.
    """


class CountPolicy(SelectionPolicy):
    """Choose count parameters among proxies.

    Check than resources number are in an interval, otherwise, raise a
    CountError.
    """

    def __init__(self, inf=0, sup=maxsize, random=False, *args, **kwargs):

        super(CountPolicy, self).__init__(*args, **kwargs)

        self.inf = inf
        self.sup = sup
        self.random = random

    class CountError(Exception):
        """Handle CountPolicy errors.
        """

    def __call__(self, *args, **kwargs):

        result = super(CountPolicy, self).__call__(*args, **kwargs)

        if isinstance(result, ProxySelection):

            len_proxies = len(result)

            if len_proxies < self.inf:
                raise CountPolicy.CountError(
                    "param count {0} ({1}) must be greater than {2}."
                    .format(result, len_proxies, self.inf)
                )

            if self.random:  # choose randomly item
                result = list(result)
                shuffle(result)
                result = result[0: self.sup - self.inf]

            else:  # choose a slice of result
                result = result[self.inf:self.sup]

            # ensure result is a policy result set
            result = ProxySelection(result)

        return result


class RandomPolicy(SelectionPolicy):
    """Choose one random item in specific parameter if parameter is a
    ProxySelection. Otherwise, Choose parameter.
    """

    def __call__(self, *args, **kwargs):

        result = super(RandomPolicy, self).__call__(*args, **kwargs)

        # do something only if result is a ProxySelection
        if isinstance(result, ProxySelection):
            if result:
                result = choice(result)

            else:
                result = None

        return result


class RoundaboutPolicy(SelectionPolicy):
    """Choose iteratively Round about proxy resource policy.

    Select iteratively resources or None if sources is empty.
    """

    def __init__(self, *args, **kwargs):

        super(RoundaboutPolicy, self).__init__(*args, **kwargs)
        # initialize index
        self.index = 0

    def __call__(self, *args, **kwargs):

        result = super(RoundaboutPolicy, self).__call__(*args, **kwargs)

        if isinstance(result, ProxySelection):
            if result:  # increment index
                index = self.index
                self.index = (self.index + 1) % len(result)
                result = result[index]

            else:
                result = None

        return result
