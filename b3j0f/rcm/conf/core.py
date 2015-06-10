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

from json import load

from os.path import exists, join

from sys import path

from b3j0f.rcm.core import Component
from b3j0f.rcm.factory.core import Factory
from b3j0f.rcm.factory import FactoryManager
from b3j0f.rcm.io import BindingManager, InputPort, OutputPort
from b3j0f.rcm.parser.core import ParserManager

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


def get_config(config_path=DEFAULT_FILE_PATH, paths=PATHS):
    """
    Get configuration file.
    """

    result = None
    if exists(config_path):
        result = load(config_path)
    else:
        for path in PATHS:
            full_config_path = join(path, config_path)
            if exists(full_config_path):
                result = load(full_config_path)
                break

    return result


BOOTSTRAP = 'bootstrap'
bootstrap = None


def get_bootstrap_component(renew=False):
    """
    Return current bootstrap component.
    """

    global bootstrap
    if bootstrap is None or renew:

        config = get_config()

        if config is not None:
            bootsrap_path = config[BOOTSTRAP]
            for path in PATHS:
                full_bootstrap_path = join(path, bootsrap_path)
                if exists(full_bootstrap_path):
                    bootstrap_config = load(full_bootstrap_path)
                    bootstrap = Factory.new_component(bootstrap_config)
                    break

    return bootstrap


class Bootstrap(Component):

    def __init__(self, factory, binding):
        pass

    @InputPort(interface=FactoryManager)
    def set_factory(self, factory):
        self.factory = factory

    @OutputPort(interface=FactoryManager)
    def get_factory(self):
        return self.factory

    @InputPort(interface=BindingManager)
    def set_binding(self, binding):
        self.binding = binding

    @OutputPort(interface=BindingManager)
    def get_binding(self):
        return self.binding

    @InputPort(interface=ParserManager)
    def set_parser(self, parser):
        self.parser = parser

    @OutputPort(interface=ParserManager)
    def get_parser(self):
        return self.binding
