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

from b3j0f.utils.version import basestring
from b3j0f.rcm.conf.core import Configuration
from b3j0f.rcm.conf.parser.core import Parser

from json import loads, load


class JSONParser(Parser):
    """Parser dedicated to json formats.

    Resource if of type dict, json object or file containing a json object.
    Such json objects have to get one type key which is the configuration type,
    and optionnaly a content key which designates inner configurations.
    Other keys are for properties.

    If you need to use a property which is named content or type, juste use a
    property name ``properties`` and put inside a json object with property
    names and values.

    For example the object:

    .. code-block:: json
        {
            "type": "itf",
            "props": {"type": false, "props": true}, "check": false,
            "content": {}
        }

    Corresponds to a component of type ``itf`` with properties ``type``,
    ``props`` and ``check`` and a default component such as a ``content``.
    """

    TYPE = 'type'  #: component configuration type in json documents.
    CONTENT = 'content'  #: component configuration content in json documents.
    PROPS = 'props'  #: component configuration props in json documents.

    def get_conf(self, resource, *args, **kwargs):

        result = None
        json_conf = None

        try:
            if isinstance(resource, dict):
                json_conf = resource
            elif isinstance(resource, basestring):
                json_conf = loads(resource)
            else:
                json_conf = load(resource)
        except Exception as e:
            raise Parser.ParserError(e)
        else:
            try:
                result = self._get_conf(json_conf)
            except Exception as e:
                raise Parser.ParserError(e)

        return result

    def _get_conf(self, json_conf):
        """Parse a json_conf document and returns a component Configuration.

        :param dict json_conf:
        :return: corresponding Configuration.
        :rtype: Configuration
        :raises: Parser.ParserError
        """

        result = Configuration()  # initialize result
        # get type
        result.type = json_conf.pop(
            JSONParser.TYPE, Configuration.DEFAULT_TYPE
        )
        # get content
        cmpt_content = json_conf.pop(JSONParser.CONTENT, None)
        if cmpt_content is not None:  # parse cmpt_content
            if isinstance(cmpt_content, dict):
                cmpt_content = [cmpt_content]
            for conf in cmpt_content:
                conf = self._get_conf(conf)
                content_by_type = result.content.setdefault(conf.type, [])
                content_by_type.append(conf)
        # get properties
        props = json_conf.pop(JSONParser.PROPS, {})
        # update json_conf with keywords props
        json_conf.update(props)
        # and set properties in result
        result.props = json_conf

        return result
