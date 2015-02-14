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

PATHS = path[:]
DEFAULT_FILE_PATH = 'b3j0f.rcm.conf'


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

from b3j0f.rcm.factory import Factory


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

from pyrcm.core import Reference, Service
from pyrcm.factory import FactoryManager
from pyrcm.binding import BindingManager
from pyrcm.parser.core import ParserManager


class Bootstrap(Component):

    def __init__(self, factory, binding):
        pass

    @Reference(interface=FactoryManager)
    def set_factory(self, factory):
        self.factory = factory

    @Service(interface=FactoryManager)
    def get_factory(self):
        return self.factory

    @Reference(interface=BindingManager)
    def set_binding(self, binding):
        self.binding = binding

    @Service(interface=BindingManager)
    def get_binding(self):
        return self.binding

    @Reference(interface=ParserManager)
    def set_parser(self, parser):
        self.parser = parser

    @Service(interface=ParserManager)
    def get_parser(self):
        return self.binding
