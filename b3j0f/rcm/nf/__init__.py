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

"""Contains definition of main controllers.
"""

__all__ = [
    'Controller',
    'ImplController',
    'IOController',
    'LifecycleController',
    'NameController',
    'RemoteController',
    'IntentController',
    'ContentController',
    'PropertyController'
]

__version__ = '0.1.0'  #: project version

from b3j0f.rcm.nf.core import Controller
from b3j0f.rcm.nf.impl import ImplController
from b3j0f.rcm.nf.io import IOController
from b3j0f.rcm.nf.lifecycle import LifecycleController
from b3j0f.rcm.nf.name import NameController
from b3j0f.rcm.nf.remote import RemoteController
from b3j0f.rcm.nf.intent import IntentController
from b3j0f.rcm.nf.content import ContentController
from b3j0f.rcm.nf.property import PropertyController
