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

        :param Configuration conf: configuration to use.
        :type conf: Configuration or configuration resource.
        :param bool cached: if True (default), use loaded component cache
            system.
        :param FactoryRegistry registry: factory registry to use.
        :return: configuration component.
        :rtype: Component
        """

        result = None

        if conf is not None:
            # instantiate a component only if the conf is validated
            if self.checker is None or self.checker.validate(conf):
                # first, instantiate all conf content with dedicated factories
                content = {}
                for contenttype in conf.content:
                    contentvalue = conf.content[contenttype]
                    component = registry.load(contentvalue, cached=cached)
                    content[contenttype] = component
                result = self.instantiator.instantiate(conf, content=content)

        return result


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
                        self.cache[component.id] = component
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

        :param Configuration conf: configuration to use.
        :type conf: Configuration or configuration resource.
        :param bool cached: if True (default), use loaded component cache
            system.
        :param str parser: parser name to use. If None (default) use the first
            parser able to parse input conf.
        :return: configuration component.
        :rtype: Component
        """

        result = self.cache.get(conf.id) if cached else None

        if result is None:
            for factory in self.factories:
                try:
                    result = factory.load(
                        conf=conf, cached=cached, registry=self
                    )
                except Factory.Error:
                    pass
                else:
                    break

        return result
