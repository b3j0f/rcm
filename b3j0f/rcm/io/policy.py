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

"""This module provides proxy selection/execution/results policy classes.

Selection
---------

A selection is a function which takes in parameters:

- port: proxy port.
- resources: port resources.
- proxies: list of port proxies.
- name: method name being executed.
- args and kwargs: respectively method varargs and keywords.

And returns one proxy or a PolicyResultSet.

Here are types of selection proxies classes:

- SelectAllPolicy: select all proxies.
- SelectFirstPolicy: select the first proxy or an empty list of proxies.
- SelectCountPolicy: select (random) proxies between [inf;sup].
- SelectRandomPolicy: select one random proxy.
- SelectRoundaboutPolicy: select iteratively a proxy among proxies. The first
    call select the first proxy. Second call, the second. When all
    proxies have been called once, the policy starts again with the first
    proxy.

Execution
---------

An execution is a function which takes in parameters:

- port: proxy port.
- resources: port resources.
- proxies: list of port proxies.
- name: method name being executed.
- args and kwargs: respectively method varargs and keywords.

And returns one result or a PolicyResultSet.

Here are default execution policy classes:

- AsyncPolicy: run asynchronously given proxies.
- BesteffortPolicy: run the first policy which does not raise Exception.

Result selection
----------------

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
    'PolicyResultSet', 'Policy', 'ParameterizedPolicy',
    'FirstPolicy', 'AllPolicy', 'CountPolicy', 'RandomPolicy',
    'RoundaboutPolicy',
    'SelectFirstPolicy', 'SelectAllPolicy', 'SelectCountPolicy',
    'SelectRandomPolicy', 'SelectRoundaboutPolicy',
    'AsyncPolicy', 'BestEffortPolicy',
    'ResultFirstPolicy', 'ResultAllPolicy', 'ResultCountPolicy',
    'ResultRandomPolicy', 'ResultRoundaboutPolicy',
]

from random import shuffle, choice

from sys import maxsize

from time import time

from collections import Callable

try:
    from threading import Thread
except ImportError:
    from dummy_threading import Thread


class PolicyResultSet(tuple):
    """In charge of embed a multiple policy result.
    """


class Policy(object):
    """In charge of applying a policy on proxy selection/execution/results.
    """

    def __call__(self, *args, **kwargs):

        raise NotImplementedError()


class ParameterizedPolicy(Policy):
    """In charge of applying a policy on a specific policy parameter designed
    by this ``name`` attribute.

    Choose the parameter by default.
    """
    def __init__(self, name, *args, **kwargs):
        """
        :param str name: parameter name.
        """

        super(ParameterizedPolicy, self).__init__(*args, **kwargs)

        self.name = name

    def __call__(self, *args, **kwargs):
        """
        :return: kwargs[self.name]
        """

        result = kwargs[self.name]

        return result


class FirstPolicy(ParameterizedPolicy):
    """Choose first value in specific parameter if parameter is
    PolicyResultSet, otherwise, return parameter.
    """

    def __call__(self, *args, **kwargs):

        param = kwargs[self.name]

        if isinstance(param, PolicyResultSet):
            result = param[0] if param else None
        else:
            result = param

        return result


class AllPolicy(ParameterizedPolicy):
    """Choose specific parameter.
    """


class CountPolicy(ParameterizedPolicy):
    """Choose count parameters among **kwargs[self.name].

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

        result = kwargs[self.name]

        if isinstance(result, PolicyResultSet):

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
            result = PolicyResultSet(result)

        return result


class RandomPolicy(ParameterizedPolicy):
    """Choose one random item in specific parameter if parameter is a
    PolicyResultSet. Otherwise, Choose parameter.
    """

    def __call__(self, *args, **kwargs):
        # default value is the parameter
        result = kwargs[self.name]

        # do something only if result is a PolicyResultSet
        if isinstance(result, PolicyResultSet):
            if result:
                result = choice(result)
            else:
                result = None

        return result


class RoundaboutPolicy(ParameterizedPolicy):
    """Choose iteratively Round about proxy resource policy.

    Select iteratively resources or None if sources is empty.
    """

    def __init__(self, *args, **kwargs):

        super(RoundaboutPolicy, self).__init__(*args, **kwargs)
        # initialize index
        self.index = 0

    def __call__(self, *args, **kwargs):
        # default result is the parameter
        result = param = kwargs[self.name]

        if isinstance(param, PolicyResultSet):
            if param:  # increment index
                result = param[self.index]
                self.index = (self.index + 1) % len(param)
            else:
                result = None

        return result


class SelectFirstPolicy(FirstPolicy):
    """Apply first policy on proxies.
    """

    def __init__(self, *args, **kwargs):

        super(SelectFirstPolicy, self).__init__(
            name='proxies', *args, **kwargs
        )


class SelectAllPolicy(AllPolicy):
    """Apply all policy on proxies.
    """
    def __init__(self, *args, **kwargs):

        super(SelectAllPolicy, self).__init__(name='proxies', *args, **kwargs)


class SelectCountPolicy(CountPolicy):
    """Apply count policy on proxies.
    """
    def __init__(self, *args, **kwargs):

        super(SelectCountPolicy, self).__init__(
            name='proxies', *args, **kwargs
        )


class SelectRandomPolicy(RandomPolicy):
    """Apply random policy on proxies.
    """
    def __init__(self, *args, **kwargs):

        super(SelectRandomPolicy, self).__init__(
            name='proxies', *args, **kwargs
        )


class SelectRoundaboutPolicy(RoundaboutPolicy):
    """Apply roundabout policy on proxies.
    """

    def __init__(self, *args, **kwargs):

        super(SelectRoundaboutPolicy, self).__init__(
            name='proxies', *args, **kwargs
        )


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
        if not isinstance(proxies, PolicyResultSet):
            proxies = [] if proxies is None else (proxies,)

        for proxy in proxies:  # execute all proxies
            proxy_rountine = getattr(proxy, routine)
            try:
                proxy_result = proxy_rountine(*args, **kwargs)
            except Exception as ex:
                if self._callback is not None:
                    # and send the occured error to the callback
                    self._callback(
                        error=ex
                    )
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
        if not isinstance(proxies, PolicyResultSet):
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


class PolicyRules(object):
    """Manage three policies of proxy selection, execution and result.
    """

    SELECT_POLICY = 'selectp'  #: selection policy attribute name
    EXEC_POLICY = 'execp'  #: execution policy attribute name
    RESULT_POLICY = 'resultp'  #: result policy attribute name

    __slots__ = [SELECT_POLICY, EXEC_POLICY, RESULT_POLICY]

    class PolicyRulesType(dict):

        def apply(self, policies, rname=None):

            raise NotImplementedError()

        def unapply(self, policies, rname=None):

            raise NotImplementedError()

        def __iadd__(self, value):

            self.apply(value)

        def __isub__(self, value):

            self.unapply(value)

        def __getitem__(self, key):

            return self.get(rname=key)

        def get(self, rname=None):
            """Get the right policy rule related to specific policy and
            routine name.

            :param str rname: routine name.
            :return: policy rule.
            """

            result = None

            # if policy is a set of rules by routine name
            if isinstance(policy, dict):
                result = policy.get(rname)
            # if policy is a rule
            elif isinstance(policy, Callable):
                result = policy

            return result

    def __init__(self, selectp=None, execp=None, resultp=None):
        """
        :param selectp: in case of not multiple port, a selectp
            chooses at runtime which proxy method to run. If it is a dict, keys
            are method names and values are callable selectp. Every
            selectp takes in parameters:
            - port: self port,
            - resources: self resources,
            - proxies: list of proxies to execute,
            - name: the called method name,
            - instance: the proxy instance,
            - args: method args,
            - kwargs: method kwargs.
        :type selectp: dict or callable
        :param execp: in case of not multiple port, a execp chooses at
            runtime how to execute a proxy method. If it is a dict, keys are
            method names and values are callable execp. Every execp
            takes in parameters:
            - port: self port,
            - resources: self resources,
            - proxies: list of proxies to execute,
            - name: the called method name,
            - instance: the proxy instance,
            - args: method args,
            - kwargs: method kwargs.
        :type execp: dict or callable
        :param resultp: in case of not multiple port, a resultp
            choose at which proxy method result to return. If it is a dict,
            keys are method names and values are callable resultp. Every
            resultp takes in parameters:
            - port: self port,
            - resources: self resources,
            - proxies: list of proxies to execute,
            - name: the called method name,
            - instance: the proxy instance,
            - args: method args,
            - kwargs: method kwargs,
            - results: method results.
        :type resultp: dict or callable
        """

        self.selectp = selectp
        self.execp = execp
        self.resultp = resultp

    @staticmethod
    def _rule(policy, rname=None):
        """Get the right policy rule related to specific policy and
        routine name.

        :param policy: policy to use.
        :type policy: dict or Callable
        :param str rname: routine name.
        :return: policy rule.
        """

        result = None

        # if policy is a set of rules by routine name
        if isinstance(policy, dict):
            result = policy.get(rname)
        # if policy is a rule
        elif isinstance(policy, Callable):
            result = policy

        return result

    def selectpr(self, rname=None):
        """Get the right selection policy rule related to a routine name.

        :param str rname: routine name.
        :return: selection policy rule.
        """

        return self._rule(policy=self.selectp, rname=rname)

    def execpr(self, rname=None):
        """Get the right execution policy rule related to a routine name.

        :param str rname: routine name.
        :return: execution policy rule.
        """

        return self._rule(policy=self.execp, rname=rname)

    def resultpr(self, rname=None):
        """Get the right result policy rule related to a routine name.

        :param str rname: routine name.
        :return: policy rule.
        """

        return self._rule(policy=self.resultp, rname=rname)

    def apply_policies(ptype, *policies):
        """Apply policies in the input policy_rules.

        :param PolicyRules policyrules: policyrules to update.
        :param list policies: list of policies to apply.
        """

        raise NotImplementedError()

    def unapply_policies(ptype, *policies):
        """Unapply policies from the input policy_rules.

        :param ptype: policy type to unapply.
        :param list policies: list of policies to apply.
        """

        raise NotImplementedError()
