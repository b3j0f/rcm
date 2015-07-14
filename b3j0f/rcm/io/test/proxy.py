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

"""Test the module b3j0f.rcm.io.proxy.
"""

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.utils.proxy import proxified_elt
from b3j0f.rcm.io.core import Port
from b3j0f.rcm.io.proxy import ProxySet


class TestProxySet(UTCase):
    """Test ProxySet.
    """

    def test_empty(self):
        """Test to instantiate a proxy set without resources.
        """

        proxyset = ProxySet(port=None, resources={}, bases=(object,))
        self.assertFalse(proxyset)
        self.assertIsNone(proxyset.port)

    def test_get_resource_name(self):
        """Test get_resource_name function.
        """

        resources = {
            '0': 1,
            '1': None,
            '2': 1,
            '3': object(),
            '4': Port(),
            '5': Port(resource=object()),
            '6': ProxySet(
                port=None, resources={0: 0, 1: 1}, bases=(object,)),
            '7': Port(resource=ProxySet(
                port=None, resources={0: 0, 1: 1}, bases=(object,))
            )
        }

        proxyset = ProxySet(port=None, resources=resources, bases=(object,))

        self.assertEqual(len(proxyset), 9)
        # number of proxies to find per resources
        counts = {
            '0': 1,
            '1': 1,
            '2': 1,
            '3': 1,
            '4': 0,
            '5': 1,
            '6': 2,
            '7': 2
        }
        # dictionary of proxy counts which will be decreased in order to check
        # if all proxies are given
        assertions = counts.copy()

        for pos, proxy in enumerate(proxyset):

            # get resource name
            rname = proxyset.get_resource_name(pos)

            # assert len of resource proxy positions
            positions = proxyset.get_proxies_pos(rname)
            self.assertEqual(len(positions), counts[rname])

            # decrement assertions
            assertions[rname] -= 1

            # check proxyfied element
            proxified = proxified_elt(proxy)
            self.assertIsNot(proxified, proxy)

        # check if all assertions are checked
        for assertion in assertions.values():
            self.assertEqual(assertion, 0)


if __name__ == '__main__':
    main()
