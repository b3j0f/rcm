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
    'BindingController',
    'LifecycleController',
    'NameController',
    'RemoteController',
    'IntentController',
    'ContentController',
    'PropertyController'
]

from b3j0f.rcm.controller.core import Controller
from b3j0f.rcm.controller.impl import ImplController
from b3j0f.rcm.controller.binding import BindingController
from b3j0f.rcm.controller.lifecycle import LifecycleController
from b3j0f.rcm.controller.name import NameController
from b3j0f.rcm.controller.remote import RemoteController
from b3j0f.rcm.controller.intent import IntentController
from b3j0f.rcm.controller.content import ContentController
from b3j0f.rcm.controller.property import PropertyController
