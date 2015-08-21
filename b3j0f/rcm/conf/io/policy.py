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

"""This module provides policy helper classes and policy result set for
application in a port proxy.
"""

__all__ = ['PolicyRulesFactory']

from b3j0f.utils.path import lookup
from b3j0f.utils.iterable import ensureiterable
from b3j0f.rcm.io.annotation import Output
from b3j0f.rcm.io.policy.core import PolicyRules
from b3j0f.rcm.ctl.property import SetProperty, GetProperty
from b3j0f.rcm.conf.factory.base import Factory


@Output()
class PolicyRulesFactory(Factory):
    """Instantiate policy rules related to policy class names.
    """

    class Error(Exception):
        """Handle PolicyRulesFactory errors.
        """

    @SetProperty(name='selectp', type=dict)
    @SetProperty(name='execp', type=dict)
    @SetProperty(name='resultp', type=dict)
    def __init__(
            self, selectp=None, execp=None, resultp=None, *args, **kwargs
    ):
        """
        :param dict selectp: selection policy class names by short name.
        :param dict execp: execution policy class names by short name.
        :param dict resultp: result policy class names by short name.
        """

        super(PolicyRulesFactory, self).__init__(*args, **kwargs)

        self.selectp = {} if selectp is None else selectp
        self.execp = {} if execp is None else execp
        self.resultp = {} if resultp is None else resultp

    @GetProperty(type=dict)
    def get_selp(self):
        """Get selection policy cls names by short names.

        :return: selection policy cls names by short names.
        :rtype: dict
        """

        return self.selectp

    @GetProperty(type=dict)
    def get_exep(self):
        """Get execution policy cls names by short names.

        :return: execution policy cls names by short names.
        :rtype: dict
        """

        return self.execp

    @GetProperty(type=dict)
    def get_resp(self):
        """Get result policy cls names by short names.

        :return: result policy cls names by short names.
        :rtype: dict
        """

        return self.resultp

    @SetProperty(type=dict)
    def set_selp(self, selectp):
        """Change of selection policy cls names by short names.

        :param dict selectp: new selection policy cls names by short names.
        """

        self.selectp = selectp

    @SetProperty(type=dict)
    def set_exep(self, execp):
        """Change of execution policy cls names by short names.

        :param dict execp: new execution policy cls names by short names.
        """

        self.execp = execp

    @SetProperty(type=dict)
    def set_resp(self, resultp):
        """Change of result policy cls names by short names.

        :param dict resultp: new result policy cls names by short names.
        """

        self.resultp = resultp

    def get_rules(self, selectp=None, execp=None, resultp=None, local=False):
        """Get a PolicyRules related to input policies.

        :param selectp: selection policy names.
        :type selectp: str(s) or dict(s)
        :param execp: execution policy names.
        :type execp: str(s) or dict(s)
        :param resultp: result policy names.
        :type resultp: str(s) or dict(s)
        :param bool local: if True (False by default), search only among
                this policies.
        :return: new PolicyRules with input policy names.
        :rtype: PolicyRules
        """

        kwargs = {}  # prepare PolicyRules kwargs

        @staticmethod
        def getkwargs(pconf, kind, local=False):
            """Get PolicyRules kwargs by kind (selectp, execp, or resultp) with
            input policy values.

            :param dict pconf: policy configuration to instantiate. Such
                configuration is of different types:

                    - str: one policy applied on all proxy routines.
                    - dict: one policy with parameters applied on all proxy
                        routines.
                    - iterable of str: several policies applied on all proxy
                        routines.
                    - iterable of dict: several policies and params applied on
                        all proxy routines.

                When a policy is a dict, it must contains the key ``_name``,
                where the value is the policy name, and optionally the key
                ``_routines`` where values are routine (regex) name(s)
                (type str(s)).
            :param str kind: policy kind among selection (selectp), execution
                (execp) or result (resultp).
            :param bool local: if True (False by default), search only among
                this policies.
            :return: set of policies by routine (regex) names.
            """

            result = {}  # policies by routine names to return

            pconf = ensureiterable(pconf, exclude=(str, dict))

            selfkind = getattr(self, kind)

            for pconfitem in pconf:
                routines = []  # routine (regex) names
                policykwargs = {}  # policy constructor kwargs

                # if policy item is a dic
                if isinstance(pconfitem, dict):
                    policyname = pconfitem.pop('_name')  # get name
                    routines = pconfitem.pop('_routines', [])  # get routines
                    routines = ensureiterable(routines, exclude=str)
                    policykwargs.update(pconfitem)  # and parameters

                try:
                    policyclsname = selfkind[policyname]

                except KeyError:
                    if local:
                        raise PolicyRulesFactory.Error(
                            'Impossible to import {0} of kind {1} from {2}.'
                            .format(policyname, kind, selfkind)
                        )

                    else:
                        try:
                            policycls = lookup(policyname)

                        except ImportError:
                            raise PolicyRulesFactory.Error(
                                'Impossible to import {0} of kind {1}.'
                                .format(policyname, kind)
                            )
                else:
                    try:
                        policycls = lookup(policyclsname)

                    except ImportError:
                        raise PolicyRulesFactory.Error(
                            'Impossible to import policy class {0}.'
                            .format(policyclsname)
                        )

                # instantiate a new policy
                policy = policycls(**policykwargs)

                # update result with routines
                if not routines:
                    routines = ['*']

                for routine in routines:
                    result.setdefault(routine, []).append(policy)

            return result

        if selectp is not None:
            kwargs['selectp'] = getkwargs(
                pconf=selectp, kind='selectp', local=local
            )

        if execp is not None:
            kwargs['execp'] = getkwargs(pconf=execp, kind='execp', local=local)

        if resultp is not None:
            kwargs['resultp'] = getkwargs(
                pconf=resultp, kind='resultp', local=local
            )

        result = PolicyRules(**kwargs)

        return result
