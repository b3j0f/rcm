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

"""Configuration core module.

Contains definition of the Configuration and the Bootstrap objects.
"""

from b3j0f.rcm.core import Component
from b3j0f.rcm.io.annotation import Output, Input
from b3j0f.rcm.conf.core import Configuration
from b3j0f.rcm.conf.parser import ParserRegistry
from b3j0f.rcm.conf.factory import FactoryRegistry


@Output()
class Bootstrap(object):
    """Bootstrap component dedicated to instantiate components thanks to
    parser and factory registry services.
    """

    class Error(Exception):
        """Handle bootstrap errors.
        """

    PARSERREGISTRY = 'parserregistry'  #: parser registry attribute name
    FACTORYREGISTRY = 'factoryregistry'  #: factory registry attribute name
    CACHE = 'cache'  #: created component cache attribute name

    @Input(itfs=ParserRegistry, param="parserregistry", mandatory=True)
    @Input(itfs=FactoryRegistry, param="factoryregistry", mandatory=True)
    @Input(itfs=Component, param="cache")
    def __init__(self, parserregistry, factoryregistry, cache=None):
        """
        :param ParserRegistry parserregistry: parser registry to use.
        :param FactoryRegistry factoryregistry: factory registry to use.
        :param Component cache: created component cache to use.
        """

        self.parserregistry = parserregistry
        self.factoryregistry = factoryregistry
        self.cache = Component() if cache is None else cache

    @Input(itfs=Component)
    def set_cache(self, cache):
        """Change of cache system.

        :param list cache: cached components.
        """

        self.cache = cache

    @Input(itfs=FactoryRegistry, mandatory=True)
    def set_factoryregistry(self, factoryregistry):
        """Change of FactoryRegistry.

        :param FactoryRegistry factoryregistry: new factory registry to use.
        """

        self.factoryregistry = factoryregistry

    @Input(itfs=ParserRegistry, mandatory=True)
    def set_parserregistry(self, parserregistry):
        """Change of ParserRegistry.

        :param ParserRegistry parserregistry: new parser registry to use.
        """

        self.parserregistry = parserregistry

    def _get_conf(self, resource, cached=True, parser=None):
        """Get resource configuration.

        :param resource: resource from where get a component configuration.
        :type resource: Configuration or object to parse with self parser
            registry or input parser.
        :param bool cached: use parser cache system.
        :param Parser parser: specific parser to use if resource is not a
            configuration.
        """

        # default result is resource if resource is a configuration
        result = resource if isinstance(resource, Configuration) else None

        if result is None:  # if resource is not a configuration, parse it
            try:
                result = self.parserregistry.parse(
                    resource=resource, cached=cached, parser=parser
                )
            except ParserRegistry.Error as prerror:
                raise Bootstrap.Error(prerror)

        return result

    def copy(self, component, cached=True):
        """Copy input component.

        :param Component component: component to copy.
        :param bool cached: if True (defaut) use the component cache system.
        """

        result = self.factoryregistry.copy(component=component, cached=cached)

        if cached:
            self.cache.set_port(result)

        return result

    def unload(self, resource, parser=None):
        """Unload a component from a resource.

        :param resource: resource from where get a component configuration to
            unload.
        :type resource: Configuration or object to parse with self parser
            registry or input parser.
        :param Parser parser: specific parser to use if resource is not a
            configuration.
        """
        # get configuration
        conf = self._get_conf(resource=resource, parser=parser)
        # unload with the factory registry
        self.factoryregistry.unload(conf)
        # remove conf from cache
        if conf.id in self.cache:
            del self.cache[conf.id]

    def load(self, resource, cached=True, parser=None):
        """Load a component from a resource.

        :param resource: resource from where get a component configuration to
            load.
        :type resource: Configuration or object to parse with self parser
            registry or input parser.
        :param bool cached: if True (defaut) use the component cache system.
        :param Parser parser: specific parser to use if resource is not a
            configuration.
        """

        result = None

        # configuration from where load a component
        conf = self._get_conf(resource=resource, cached=cached, parser=parser)
        # get component from factory
        result = self.factoryregistry.load(conf=conf, cached=cached)
        # save in cache if necessary
        if cached:
            self.cache.set_port(result)

        return result
