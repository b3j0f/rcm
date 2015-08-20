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

from b3j0f.utils.version import basestring
from b3j0f.rcm.prop.core import Property
from b3j0f.rcm.io.annotation import Output, Input
from b3j0f.rcm.conf.parser import Parser

from urllib import get

from sys import path
from os.path import join, abspath, expanduser, exists


@Output()
class ParserRegistry(object):
    """Registry of parsers.

    Contains a reference to directories paths and a cache system in order to
    bind configuration with resource ids.
    """

    class Error(Exception):
        """Handle parsing errors.
        """

    PARSERS = 'parsers'  #: parsers attribute name
    CACHE = 'cache'  #: cache attribute name
    PATHS = 'paths'  #: paths attribute name

    DEFAULT_PATHS = path[:]  #: default paths to use (runtime paths)

    @Input(itfs=Parser, mandatory=True, many=True, name='parsers')
    @Property(type=str, name='paths')
    def __init__(self, parsers, paths=DEFAULT_PATHS, cache=None):
        """
        :param list parsers: parsers to use.
        :param paths: directory paths from where find resources. Default is
            runtime paths.
        :type paths: str(s)
        :param dict cache: cache system (set of resource by configuration).
        """

        super(ParserRegistry, self).__init__()

        self.parsers = parsers
        self.paths = paths[:]
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

    @Property(type=str)
    def set_paths(self, paths):
        """Change of paths.

        :param paths: new paths to use.
        :type paths: str(s)
        """

        self.paths = paths

    def _readcontent(self, resource, getter=None, reader=None, paths=None):
        """Try to read configuration content from input resource.

        :param resource: resource from where get configuration.
        :param bool cached: use cache system.
        :param str parser: parser name to use.
        :param list paths: paths from where find directories. Default is self
            paths.
        :param reader: file reader function which takes in parameters a file
            path. Useful to read with dedicated encoding parameter or in
            uncompressing the content.
        :param getter: url getter function which takes in parameters an url. It
            allows to use a requests session for example if an authentification
            is required: getter=lambda url: requests.Session(...).get(url)
        """

        result = resource  # default result is the resource

        try:  # is resource an URL ?
            if getter is None:
                result = get(result).read()
            else:
                result = getter(resource)

        except Exception:
            # is resource a file
            rscpath = None  # final resource path

            if exists(resource):  # if resource is an absolute path
                rscpath = resource

            else:  # if resource is a relative path
                paths = self.paths if paths is None else paths

                for _path in paths:
                    absrscpath = abspath(expanduser(join(_path, resource)))

                    if exists(abspath):
                        rscpath = absrscpath
                        break

                if rscpath is not None:  # if a path is found, read the content

                    if reader is None:
                        with open(rscpath) as rscfile:
                            result = rscfile.read()

                    else:
                        result = reader(rscpath)

        return result

    def get_conf(
            self, resource, cached=True, parser=None, paths=None,
            reader=None, getter=None
    ):
        """Get resource configuration thanks to input parsers.

        :param resource: resource from where get configuration. It could be a
            configuration (dict) or a parsing content or a file or an url.
        :type resource: dict or str
        :param bool cached: use cache system.
        :param parser: parser (name) to use.
        :type parser: Parser
        :param list paths: paths from where find directories. Default is self
            paths.
        :param reader: file reader function which takes in parameters a file
            path and returns the file content such as a string. The file path
            is of the form '{dir}/{resource}' where ``dir`` is in (self) paths
            and returns a string. Useful to read with dedicated encoding
            parameter or in uncompressing the content.
        :param getter: url getter function which takes in parameters an url and
            returns the resource content such as a string. Used in case of
            resource is an URL. It allows to use a requests session for
            example if an authentification is required: getter=lambda url:
            requests.Session(...).get(url).
        :return: resource configuration.
        :rtype: dict
        """

        result = resource if isinstance(resource, dict) else None

        if result is None:
            # if resource is a string
            if isinstance(resource, basestring):
                # first, check if resource is in cache
                if cached and resource in self.cache:
                    result = self.cache[resource]
                else:  # try to find a resource
                    # try to read resource content if resource is a file
                    content = self._readcontent(
                        resource=resource, getter=getter, reader=reader,
                        paths=paths
                    )

                    if parser is None:  # try to find a useful parser
                        for parser in self.parsers:
                            try:
                                result = parser.parse(content)
                            except Parser.Error:
                                pass
                            else:
                                break

                    else:  # use specific parser
                        if isinstance(parser, basestring):
                            parser = self.parsers.get(parser)
                        result = parser.parse(content)

        if result is None:
            raise ParserRegistry.Error(
                "{0} failed to parse the resource {1}".format(self, resource)
            )
        elif cached:  # if cached, save the configuration in cache
            self.cache[resource] = result

        return result
