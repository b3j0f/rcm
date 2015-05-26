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

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.rcm.core import Component
from b3j0f.rcm.binding.core import Interface, Resource


class TestResource(UTCase):
    """Test Resource.
    """

    def test_noitfs(self):
        """Test itfs consistency with default initialization parameter.
        """
        resource = Resource()

        self.assertEquals(len(resource.itfs), 1)
        self.assertIs(resource.itfs[0].pycls, object)

    def test_itfs(self):
        """Test itfs consistency with initialization parameter.
        """
        itfs = (1)
        resource = Resource(itfs=itfs)
        self.assertEqual(resource.itfs, itfs)

    def test_proxy(self):
        """Test resource proxy getter.
        """

        resource = Resource()
        self.assertIsNone(resource.proxy, resource.proxy)


class TestInterface(UTCase):
    """Test Interface.
    """

    def setUp(self):

        self.interface = Interface()

    def test_none(self):
        """Test to set a None value.
        """

        self.interface = Interface()
        self.assertIsNone(self.interface.value, None)
        self.assertIs(self.interface.pycls, object)

    def test_inconsistent_value(self):
        """Test to instantiate an interface with an inconsistent value.
        """

        self.assertRaises(NotImplementedError, Interface, "")

    def test_is_sub_itf(self):
        """Test is_sub_itf method.
        """

        baseitf = Interface(value=object)
        subitf = Interface(value=Component)
        subsubitf = Interface(value=Resource)

        self.assertFalse(baseitf.is_sub_itf(subitf))
        self.assertFalse(baseitf.is_sub_itf(subsubitf))

        self.assertFalse(subitf.is_sub_itf(subsubitf))

        self.assertTrue(subsubitf.is_sub_itf(baseitf))
        self.assertTrue(subsubitf.is_sub_itf(subitf))

        self.assertTrue(subitf.is_sub_itf(baseitf))

if __name__ == '__main__':
    main()
