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

from b3j0f.annotation import Annotation
from b3j0f.rcm import Component
from b3j0f.rcm.controller.binding import BindingController
from b3j0f.rcm.controller.intent import IntentController
from b3j0f.rcm.controller.lifecycle import LifecycleController
from b3j0f.rcm.controller.parameter import ParameterController
from b3j0f.rcm.controller.name import NameController
from b3j0f.rcm.controller.scope import ScopeController
from b3j0f.rcm.controller.business import BusinessController
from b3j0f.rcm.controller.remote import RemoteController


class Configurate(Annotation):

    def __init__(self, *controllers, **interfaces):

        super(Configurate, self).__init__()
        self.controllers = controllers
        self.interfaces = interfaces


@Configurate(
    IntentController,
    LifecycleController,
    ParameterController,
    NameController,
    ScopeController,
    BusinessController,
    BindingController)
class BaseComponent(Component):
    """
    Component with default controllers.
    """

    pass


@BaseComponent(RemoteController)
class RemoteComponent(Component):

    pass
