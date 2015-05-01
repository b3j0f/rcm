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

"""This module provides dynamic proxy selection/execution.

Selection
---------

A selection is a function which takes in parameters:
- port: proxy port.
- resources: port resources.
- proxies: list of port proxies.
- name: method name being executed.
- args and kwargs: respectively method varargs and keywords.

And returns a list of proxies.

Here are types of proxies:
- all: select all proxies.
- first: select the first proxy or an empty list of proxies.
- count: select (random) proxies between [inf;sup].
- random: select one random proxy.
- roundabout: select iteratively a resource among resources. The first call
select the first resource. Second call, the second. When all resources have
been called once, the policy starts again with the first resource.

Execution
---------

An execution is a function which takes in parameters:
- port: proxy port.
- resources: port resources.
- proxies: list of port proxies.
- name: method name being executed.
- args and kwargs: respectively method varargs and keywords.

And returns a list of proxy results.

- async: run asynchronously
- roundabout:
- besteffort:

Multiple
--------

A multiple policy returns a list of proxies among a list of resources.

- all: select all resources.
- random: select random resources.
- count: select a number of resources between [inf; sup].
- dynamic: select resources which are checked by a function filter.
"""

__all__ = [
    'all', 'first', 'count', 'random', 'roundabout',
    'async', 'besteffort'
]

from random import randint, choice

from sys import maxsize


try:
    from threading import Thread
except ImportError:
    from dummy_threading import Thread


def first(proxies, *args, **kwargs):
    """One policy resource policy.

    Select first resource or empty selection if resources is empty.
    """

    result = proxies[0:1]

    return result


def all(proxies, *args, **kwargs):
    """All dynamic selection.
    """

    return proxies


def count(inf=0, sup=maxsize, random=False):
    """Count proxy resource policy.

    Check than resources number are in an interval.
    """

    class CountError(Exception):
        pass

    def dynselect(self, proxies, *args, **kwargs):

        len_proxies = len(proxies)

        if len_proxies < self.inf or len_proxies > self.sup:
            raise CountError(
                "Proxies count {0} not in [{1}; {2}]."
                .format(proxies, self.inf, self.sup)
            )

        if random:  # choose randomly proxies
            count_to_remove = len_proxies - min(sup - inf, len_proxies)
            for i in range(count_to_remove):
                index = randint(0, len(proxies))
                proxies.pop(index)
            result = proxies
        else:  # choose a slice of proxies
            result = proxies[inf:sup]

        return result


def random(proxies, *args, **kwargs):
    """One Random proxy resource policy.

    Select one random proxy or None if resources is empty.
    """

    result = None

    if proxies:
        result = (choice(proxies),)

    return result


def roundabout():
    """Round about proxy resource policy.

    Select iteratively resources or None if sources is empty.
    """

    index = 0

    def dynselect(proxies, *args, **kwargs):

        global index
        index = (index + 1) % len(proxies)
        return proxies[index:index + 1]


def async(callback):
    """Asynchronous dynamic execution.

    :param callback: proxy method execution callback which takes in parameters
        the method result and all dynexec parameters.
    """

    def execproxies(proxies, name, args, kwargs, **keywords):
        for p in proxies:
            callback(
                name=name,
                args=args,
                kwargs=kwargs,
                result=getattr(p, name)(*args, **kwargs),
                **keywords
            )

    def dynexec(proxies, name, args, kwargs, **keywords):
        # create a thread which call callback(instance.name(*args, **kwargs))
        thread = Thread(
            lambda:
            execproxies(
                proxies=proxies,
                name=name,
                args=args,
                kwargs=kwargs,
                **keywords
            )
        )
        # start the thread
        thread.start()

    return dynexec


def besteffort(proxies, name, *args, **kwargs):
    """Best effort proxy resource policy.

    Select first resources which does not raise an Error, otherwise last error
        or None if no sources.
    """

    result = None

    for proxy in proxies:
        method = getattr(proxy, name)
        try:
            result = method(*args, **kwargs)
        except Exception:
            pass
        else:
            break

    return result
