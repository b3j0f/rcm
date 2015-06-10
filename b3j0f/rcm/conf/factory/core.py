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

from b3j0f.rcm.nf.impl import Input, Output
from b3j0f.rcm.conf.parse import Parser
from b3j0f.rcm.conf.check import Checker
from b3j0f.rcm.conf.instance import Instantiator


@Output()
class Factory(object):
    """In charge of instantiate components from configuration.

    By default, a factory have ports where names correspond to configuration
    content type names.
    """

    class Error(Exception):
        """Handle Instantiation errors.
        """

    @Input(many=True, itfs=Parser)
    def set_parsers(self, parsers):

        self.parsers = parsers

    @Input(mandatory=False, itfs=Checker)
    def set_validator(self, validator):

        self.validator = validator

    @Input(itfs=Instantiator)
    def set_instantiator(self, instantiator):

        self.instantiator = instantiator

    @Input(mandatory=False, itfs='b3j0f.rcm.conf.factory.Factory')
    def set_factories(self, factories):

        self.factories = factories

    def get_component(self, conf):
        """Instantiate a new Component from input conf.

        :param b3j0f.rcm.conf.core.Configuration conf: configuration to use.
        :return: configuration component.
        :rtype: Component
        """

        result = None

        for parser in self.parsers:
            try:
                conf = parser.get_conf(conf)
            except Parser.ParserError:
                pass
            else:
                if self.validator is None or self.validator.validate(conf):
                    result = self.instantiator.instantiate(conf)
                    for content in conf.content:
                        factory = self.factories.get(content.type)
                        factory.get_component(content)
                    break
        else:
            raise

        return result
