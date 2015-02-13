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

"""
Regroup all controller annotations.
"""

__all__ = [
    'ImplAnnotation', 'Controllers',  # Controller annotation
    'Impl', 'Context',  # impl controller annotations
    'Property', 'GetProperty', 'SetProperty',  # property controller annotation
    'Binding', 'Input', 'Output',  # binding controller annotations
    'Lifecycle', 'Before', 'After',  # lifecycle controller annotations
    'Name', 'GetName', 'SetName',  # name controller annotations
]

from b3j0f.rcm.controller.core import ImplAnnotation, Controllers
from b3j0f.rcm.controller.impl import (
    Impl, Context, Property, GetProperty, SetProperty
)
from b3j0f.rcm.controller.binding import Binding, Input, Output
from b3j0f.rcm.controller.lifecycle import Lifecycle, Before, After
from b3j0f.rcm.controller.name import Name, GetName, SetName
