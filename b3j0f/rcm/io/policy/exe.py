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

"""This module provides proxy execution policy classes.

An execution is a function which takes in parameters:

- port: proxy port.
- resources: port resources.
- proxies: list of port proxies.
- name: method name being executed.
- args and kwargs: respectively method varargs and keywords.

And returns one result or a PolicyResultSet.

Here are default execution policy classes:

- AsyncPolicy: run asynchronously given proxies.
- BestEffortPolicy: run the first policy which does not raise Exception.
- StatelessPolicy: run proxies with one instance per call.
"""

__all__ = ['AsyncPolicy', 'BestEffortPolicy', 'StatelessPolicy']

from random import shuffle

from sys import maxsize

from time import time

try:
    from threading import Thread

except ImportError:
    from dummy_threading import Thread

from b3j0f.rcm.io.proxy import ProxySet
from b3j0f.rcm.io.policy.core import Policy


class AsyncPolicy(Policy):
    """Asynchronous dynamic execution policy.

    A callback is used in order to be notified when all proxy are executed.
    Such callback takes in parameter:
    - result: proxy execution result.
    - error: proxy execution error.

    In a multi task concern, the join method permits to wait until all proxy
    are executed.
    """

    _CALLBACK = '_callback'  #: private callback attribute name
    _THREAD = '_thread'  #: private thread attribute name

    def __init__(self, callback=None, *args, **kwargs):
        """
        :param callable callback: callable object which will get proxy
            execution results.
        """

        super(AsyncPolicy, self).__init__(*args, **kwargs)

        # initialize private attributes
        self._thread = None

        # set callback
        self._callback = callback

    def __call__(self, *args, **kwargs):
        # create a thread which execute self.exec_proxies
        self._thread = Thread(
            target=self.exec_proxies, args=args, kwargs=kwargs
        )
        # start the thread
        self._thread.start()

    def exec_proxies(self, proxies, routine, *args, **kwargs):
        """Execute iteratively all proxies and use result in self callback.

        :param proxies: proxies to execute.
        :param str routine: routine name of proxies to execute.
        """

        # ensure proxies is a list of proxies
        if not isinstance(proxies, ProxySet):
            proxies = [] if proxies is None else (proxies,)

        for proxy in proxies:  # execute all proxies
            proxy_rountine = getattr(proxy, routine)

            try:
                proxy_result = proxy_rountine(*args, **kwargs)

            except Exception as ex:
                if self._callback is not None:
                    # and send the occured error to the callback
                    self._callback(error=ex)

            else:
                if self._callback is not None:
                    # and send result to the callback
                    self._callback(
                        result=proxy_result
                    )

    def join(self):
        """Wait until all proxy are executed.
        """

        if isinstance(self._thread, Thread):
            self._thread.join()


class BestEffortPolicy(Policy):
    """Best effort proxy resource policy.

    Select first resources which does not raise an Error, otherwise last error
        or None if no sources.
    Raises last raised exception.
    """

    class TimeoutError(Exception):
        """Raised when a timeout occures.
        """
        pass

    class MaxTryError(Exception):
        """Raised when a max try is passed.
        """

        MAXTRY = 'maxtry'  #: maxtry attribute name
        RANDOM = 'random'  #: random attribute name
        TIMEOUT = 'timeout'  #: timeout attribute name

    def __init__(
            self, maxtry=maxsize, random=False, timeout=None, *args, **kwargs
    ):
        """
        :param int maxtry: maximum try. sys.maxsize by default.
        :param bool random: if True (False by default), choose randomly a proxy
            on each step.
        :param int timeout: maximal timeout before stopping to execute proxies
            if not None (default).
        """

        super(BestEffortPolicy, self).__init__(*args, **kwargs)

        self.maxtry = maxtry
        self.random = random
        self.timeout = timeout

    def __call__(self, proxies, routine, *args, **kwargs):

        # initialize the default result
        result = None

        # ensure proxies is an iterable of proxies
        if not isinstance(proxies, ProxySet):
            proxies = () if proxies is None else (proxies,)

        # initialiaze policy parameters
        maxtry = self.maxtry

        # if random, shuffle proxies
        random = self.random
        if random:
            proxies = list(proxies)
            shuffle(proxies)

        proxies_iterator = iter(proxies)

        # if timeout, save last_time with current time
        timeout = self.timeout
        if timeout is not None:
            tick = time()

        # run proxies
        while True:

            # check for maxtry
            if maxtry <= 0:
                raise BestEffortPolicy.MaxTryError()

            # check for timeout condition
            if timeout is not None and timeout > (time() - tick):
                raise BestEffortPolicy.TimeoutError()

            # choose next proxy
            try:
                proxy = next(proxies_iterator)

            except StopIteration:
                break  # stop to execute proxies if no more proxies to run

            else:
                method = getattr(proxy, routine)  # get the right proxy method

                try:
                    result = method(*args, **kwargs)

                except Exception:
                    pass  # continue iteration on errors

                else:
                    break  # stop as soon as a proxy is executed without error

                maxtry -= 1  # decrement maxtry

        return result


class StatelessPolicy(Policy):
    """Exec policy in charge of given a new instance per call.
    """

    def __call__(self, routine, instance, *args, **kwargs):

        # get instance cls
        cls = type(instance)
        # instantiate a new proxy
        proxy = cls()

        proxyroutine = getattr(proxy, routine)

        return proxyroutine(*args, **kwargs)
