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

from sys import path


PATHS = path[:]
DEFAULT_FILE_PATH = 'b3j0f.rcm.conf'


class Configuration(object):
    """Component configuration object.

    It provides a description for component instantiation/definition.

    This description contains attributes:

        - type: component type, like a Port, or Interface, etc. Default is
            ``component``.
        - props: dict of component properties by name.
        - content: dict of inner component configurations by type.
    """

    TYPE = 'type'  #: configuration type attribute name
    PROPS = 'props'  #: configuration props attribute name
    CONTENT = 'content'  #: configuration content attribute name

    DEFAULT_TYPE = 'component'  #: default type value

    __slots__ = (TYPE, PROPS, CONTENT)

    def __init__(self, _type=DEFAULT_TYPE, props=None, content=None):

        self.type = _type
        self.props = props if props else {}
        self.content = content if content else {}
