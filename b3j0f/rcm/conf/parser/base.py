# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2014 Jonathan Labéjof <jonathan.labejof@gmail.com>
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

"""Base module for parser services.
"""

from b3j0f.rcm.io.annotation import Output, Input
from b3j0f.rcm.conf.core import Configuration


@Output()
class Parser(object):
    """Parse a resource and returns a component configuration.
    """

    class Error(Exception):
        """Handle parsing errors.
        """

    def get_conf(self, resource):
        """
        :param resource: resource to parse.
        :return: resource configuration.
        :rtype: Configuration
        :raises: ParserError in case of a parser error happened.
        """

        raise NotImplementedError()


@Output()
class ParserRegistry(object):
    """Registry of parsers.
    """

    class Error(Exception):
        """Handle parsing errors.
        """

    PARSERS = 'parsers'  #: parsers attribute name
    CACHE = 'cache'  #: cache attribute name

    @Input(itfs=Parser, mandatory=True, many=True)
    def __init__(self, parsers, cache=None):
        """
        :param list parsers: parsers to use.
        """

        super(ParserRegistry, self).__init__()

        self.parsers = parsers
        self.cache = {} if cache is None else cache

    @Input(itfs=Parser, mandatory=True, many=True)
    def set_parsers(self, parsers):
        """Change of parsers.

        :param list parsers: new parsers to use.
        """

        self.parsers = parsers

    def set_cache(self, cache):
        """Change of cache.

        :param dict cache: new cache to use.
        """

        self.cache = cache

    def get_conf(self, resource, cached=True, parser=None):
        """Get resource configuration thanks to input parsers.

        :param resource:
        :param bool cached: use cache system.
        :param str parser: parser name to use.
        """
        result = resource if isinstance(resource, Configuration) else None

        if result is None:
            parsers = ()  # get parsers to use
            if parser is not None:  # in case of specific parser to use
                parsers = [self.parsers[parser]]
            else:
                parsers = self.parsers.keys()

            for parser in parsers:  # try to parse the resource
                try:
                    result = parser.parse(resource, cached=cached, parser=None)
                except Parser.Error:
                    pass
                else:
                    if result is not None:
                        break

        if result is None:
            raise ParserRegistry.Error(
                "{0}: Impossible to parse the resource {1}".format(
                    self, resource
                )
            )
        elif cached:  # if cached, save the configuration in cache
            self.cache[result.id] = result

        return result
