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

"""Factory Registry module.

Contains the implementation of the FactoryRegistry.
"""

from b3j0f.rcm.io.annotation import Input, Output
from b3j0f.rcm.conf.core import TYPE, UID
from b3j0f.rcm.conf.factory.base import Factory


@Output()
class FactoryRegistry(object):
    """In charge of instantiate components from a set of factories.

    By default, a factory registry have ports where names correspond to
    configuration content type names.
    """

    class Error(Exception):
        """Handle Instantiation errors.
        """

    def __init__(self, factories, cache=None):
        """
        :param dict factories: factories.
        :param dict cache: cache system to use.
        """

        super(FactoryRegistry, self).__init__()

        self.factories = {} if factories is None else factories
        self.cache = {} if cache is None else cache

    @Input(mandatory=False, itfs=Factory)
    def set_factories(self, factories):
        """Sub factories by type.

        For example, {'binding': BindingFactory() , ...} for a port factory.
        """

        self.factories = factories

    def set_cache(self, cache):
        """Change of cache.

        :param dict cache:
        """

        self.cache = cache

    def copy(self, component, cached=True):
        """Copy input component.

        :param Component component: component to copy.
        :return: input component copy.
        :rtype: Component.
        """

        result = None

        for factory in self.factories:
            try:
                result = factory.copy(component=component)
            except Factory.Error:
                pass
            else:
                if result is not None:
                    if cached:
                        self.cache[component.uid] = component
                    break

        return result

    def unload(self, component):
        """Unload a component.

        :param Component component: component to unload.
        """

        if component.id in self.cache:  # if component is in cache
            del self.cache[component.id]  # clean cache
            # remove component ports
            for port in list(component.values()):
                del component[port]
                # unload recursively to not used ports
                if not port._rports:
                    self.unload(port)
            # remove component reversed ports
            for rport in list(component._rports):
                del rport[component]
            # try to delete the component
            del component

    def load(self, conf, cached=True):
        """Instantiate a new Component from input conf.

        :param dict conf: configuration to use.
        :param bool cached: if True (default), use loaded component cache
            system.
        :param str parser: parser name to use. If None (default) use the first
            parser able to parse input conf.
        :return: configuration component.
        :rtype: Component
        """

        result = self.cache.get(conf.get(UID)) if cached else None

        if result is None:
            # get conf type factory
            conftype = conf.get(TYPE, 'component')
            factory = self.factories.get(conftype)

            if factory is None:
                raise FactoryRegistry.Error(
                    "{0} has not found factory to load {1}."
                    .format(self, conf)
                )

            else:
                result = factory.load(
                    conf=conf, cached=cached, registry=self
                )

        return result
