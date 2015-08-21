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

"""This module provides the port factory.
"""

__all__ = ['PortFactory']

from b3j0f.rcm.io.annotation import Output, Input
from b3j0f.rcm.conf.io.binding import BindingFactoryRegistry
from b3j0f.rcm.conf.io.itf import InterfaceFactoryRegistry
from b3j0f.rcm.conf.io.policy import PolicyRulesFactory


@Output()
class PortFactory(object):
    """Instantiate Port.
    """

    class Error(Exception):
        """Handle PortFactory errors.
        """

    @Input(
        name='bindingfactoryregistry', itfs=BindingFactoryRegistry,
        mandatory=True
    )
    @Input(name='policyrulesfactory', itfs=PolicyRulesFactory, mandatory=True)
    @Input(
        name='itffactoryregistry', itfs=InterfaceFactoryRegistry,
        mandatory=True
    )
    def __init__(
            self,
            bindingfactoryregistry, policyrulesfactory, itffactoryregistry
    ):
        """
        :param BindingFactoryRegistry bindingfactoryregistry: binding factory
            registry to use.
        :param PolicyRulesFactor policyrulesfactory: policy rules factory to
            use.
        :param InterfaceFactoryRegistry itffactoryregistry: itf factory
            registry to use.
        """

        self.bindingfactoryregistry = bindingfactoryregistry
        self.policyrulesfactory = policyrulesfactory
        self.itffactoryregistry = itffactoryregistry

    @Input(
        name='bindingfactoryregistry', itfs=BindingFactoryRegistry,
        mandatory=True
    )
    def set_bindingfactoryregistry(self, bindingfactoryregistry):
        """Change of BindingFactoryRegistry.

        :param BindingFactoryRegistry bindingfactoryregistry: binding factory
            registry to use.
        """

        self.bindingfactoryregistry = bindingfactoryregistry

    @Input(name='policyrulesfactory', itfs=PolicyRulesFactory, mandatory=True)
    def set_policyrulesfactory(self, policyrulesfactory):
        """Change of PolicyRulesFactory.

        :param PolicyRulesFactor policyrulesfactory: policy rules factory to
            use.
        """

        self.policyrulesfactory = policyrulesfactory

    @Input(
        name='itffactoryregistry', itfs=InterfaceFactoryRegistry,
        mandatory=True
    )
    def set_itffactoryregistry(self, itffactoryregistry):
        """Change of InterfaceFactoryRegistry.

        :param InterfaceFactoryRegistry itffactoryregistry: itf factory
            registry to use.
        """

        self.itffactoryregistry = itffactoryregistry
