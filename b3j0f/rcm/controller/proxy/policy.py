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

"""This module provides classes in charge of executing proxy resource policy.

Policies are dedicated to select proxy resources where proxy objects have
several sources from where get resources.

Default policy values are:

- One: select the first resource.
- All: select all resources.
- RoundAbout: select iteratively a resource among resources. The first call
select the first resource. Second call, the second. When all resources have
been called once, the policy starts again with the first resource.
- Random: select a random resource.
- BestEffort: select the first resource which does not raise an Error.
"""

__all__ = [
    'Policy',
    'OnePolicy', 'AllPolicy',
    'RoundAboutPolicy', 'RandomPolicy',
    'BestEffortPolicy'
]

from random import randint

from b3j0f.utils.path import lookup


def get_policy(name, path=None):
    """Get policy class.

    >>> get_policy(name='all').__name__
    b3j0f.rcm.controller.policy.AllPolicy.

    :param str name: policy name. Related class name must finish by 'Policy'.
    :param str path: policy class module. If None, use __file__ path.
    :return: Policy class.
    :rtype: type
    """

    if path is None:
        path = __file__[:-3]

    full_name = "{0}.{1}Policy".format(path, name.capitalize())

    result = lookup(full_name)

    return result


class Policy(object):
    """Proxy resource policy.
    """

    def get_resource(self, sources, stateful):

        raise NotImplementedError()


class OnePolicy(Policy):
    """One policy resource policy.

    Select first resource or None if sources is empty.
    """

    def get_resource(self, sources, stateful):

        result = None

        if sources:
            result = sources[0].get_resource(stateful=stateful)

        return result


class AllPolicy(Policy):
    """All proxy resource policy.

    Select all resources.
    """

    def get_resource(self, sources, stateful):

        result = [
            source.get_resource(stateful=stateful) for source in sources
        ]

        return result


class RandomPolicy(Policy):
    """Random proxy resource policy.

    Select a random resource or None if sources is empty.
    """

    def get_resource(self, sources, stateful):

        result = None

        if sources:
            source = sources[randint(0, len(sources) - 1)]
            result = source.get_resource(stateful=stateful)

        return result


class RoundAboutPolicy(Policy):
    """Round about proxy resource policy.

    Select iteratively resources or None if sources is empty.
    """

    def __init__(self, *args, **kwargs):

        super(RoundAboutPolicy, self).__init__(*args, **kwargs)

        self.index = 0

    def get_resource(self, sources, stateful):

        result = None

        if sources:  # if sources exist, increment index counter
            index = self.index + 1
            index %= len(sources)
            self.index = index
            source = sources[index]
            # and get related resource
            result = source.get_resource(stateful=stateful)

        return result


class BestEffortPolicy(Policy):
    """Best effort proxy resource policy.

    Select first resources which does not raise an Error, otherwise last error
        or None if no sources.
    """

    def get_resource(self, sources, stateful):

        result = None

        for source in sources:
            try:
                resource = source.get_resource(stateful)
            except Exception:
                pass
            else:
                result = resource

        return result
