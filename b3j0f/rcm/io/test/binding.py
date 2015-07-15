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

"""Test the module b3j0f.rcm.io.core.
"""

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.rcm.io.core import Port
from b3j0f.rcm.io.desc import Interface
from b3j0f.rcm.io.binding import Binding


class BindingTest(UTCase):
    """Test Binding.
    """

    class TestBinding(Binding):
        """Test binding.
        """

        def __init__(self, *args, **kwargs):

            super(BindingTest.TestBinding, self).__init__(*args, **kwargs)

            self.count = 0

        def _renewproxy(self):

            self.count = 1

    def setUp(self):
        """Initialize test properties.
        """

        self.binding = BindingTest.TestBinding()

    def test_update_input_itfs(self):
        """Test if a binding updates its interface if a port is bound to the
        Binding.
        """

        self.assertIsNone(self.binding.itfs)

        itfs = (Interface(),)

        port = Port(itfs=itfs)
        port.set_port(port=self.binding)

        self.assertEqual(self.binding.itfs, itfs)

    def test_update_output_itfs(self):
        """Test if a binding updates its interface if a port is bound to the
        Binding.
        """

        self.assertIsNone(self.binding.itfs)

        itfs = (Interface(),)

        port = Port(itfs=itfs)
        self.binding.set_port(port=port)

        self.assertEqual(self.binding.itfs, itfs)

    def test_update_proxy(self):
        """Test if a binding updates its proxy when a new port is bound to it.
        """

        self.assertEqual(self.binding.count, 0)

        port = Port()
        self.binding.set_port(port=port)

        self.assertEqual(self.binding.count, 1)


if __name__ == '__main__':
    main()
