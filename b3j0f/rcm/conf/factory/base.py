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

"""Base module for the factory package.

Contains the implementation of the abstract Factory.
"""

from b3j0f.rcm.io.annotation import Input, Output
from b3j0f.rcm.conf.check import Checker
from b3j0f.rcm.conf.instance import Instantiator


@Output()
class Factory(object):
    """In charge of instantiating/deleting components from configuration.

    By default, a factory have ports where names correspond to configuration
    content type names.
    """

    @Input(itfs=Checker, param='checked')
    @Input(mandatory=True, itfs=Instantiator, param='instantiator')
    def __init__(self, checker, instantiator):
        """
        :param Checker checker: checker.
        :param Instantiator instantiator: instantiator.
        """

        super(Factory, self).__init__()

        self.checker = {} if checker is None else checker
        self.instantiator = {} if instantiator is None else instantiator

    class Error(Exception):
        """Handle Instantiation errors.
        """

    @Input(itfs=Checker)
    def set_validator(self, checker):
        """Change of checker.

        :param Checker checker: new checker to use.
        """

        self.checker = checker

    @Input(itfs=Instantiator, mandatory=True)
    def set_instantiator(self, instantiator):
        """Change of instantiator.

        :param Instantiator instantiator: new instantiator to use.
        """

        self.instantiator = instantiator

    def unload(self, component):
        """Unload a component.
        """

        self.instantiator.unload(component=component)

    def copy(self, component):
        """Copy input component.

        :param Component component: component to copy.
        :return: input component copy.
        :rtype: Component.
        """

        result = self.instantiator.copy(component=component)

        return result

    def load(self, conf, cached=True, registry=None):
        """Instantiate a new Component from input conf.

        :param conf: configuration to use.
        :type conf: dict, str, bool, list or number
        :param bool cached: if True (default), use loaded component cache
            system.
        :param FactoryRegistry registry: factory registry to use.
        :return: configuration component.
        :rtype: Component
        """

        result = None

        if conf is not None:
            # instantiate a component only if the conf is checked
            if self.checker is None or self.checker.check(conf):
                # first, instantiate all conf ports with dedicated factories
                if isinstance(conf, dict):  # if conf may have ports
                    for portname in list(conf):
                        if portname in registry.factories:
                            portconf = conf[portname]
                            port = registry.load(
                                conf=portconf, cached=cached, factory=portname
                            )
                            conf[portname] = port
                self.instantiator.instantiate(conf=conf)

        return result
