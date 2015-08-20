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

from b3j0f.rcm.io.annotation import Output


@Output()
class Parser(object):
    """Parse a resource and returns a component configuration.
    """

    class Error(Exception):
        """Handle parsing errors.
        """

    def get_conf(self, raw):
        """Get input raw configuration (inverse of get_raw).

        :param str raw: raw to parse.
        :return: raw configuration.
        :rtype: dict
        :raises: ParserError in case of a parser error happened.
        """

        raise NotImplementedError()

    def get_raw(self, conf):
        """Get conf raw (inverse of get_conf).

        :param dict conf: configuration to rawify.
        :return: rawed configuration.
        :rtype: str
        """

        raise NotImplementedError()
