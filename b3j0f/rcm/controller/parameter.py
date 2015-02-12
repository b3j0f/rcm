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

from b3j0f.rcm.controller import ComponentController


class ParameterController(ComponentController):
    """
    Dedicated to manage component parameters.
    """

    def __init__(self, component, **kwargs):

        super(ParameterController, self).__init__(component=component)
        self._params = kwargs.copy()

    def get_parameter_names(self):
        """
        Get component parameter names
        """

        return self._params.keys()

    def get_parameter(self, name):
        """
        Get component parameter which is registered with the input name.
        """

        return self._params[name]

    def set_parameter(self, name, parameter):
        """
        Change parameter which is associated to the input name.
        """

        self._params[name] = parameter

    @staticmethod
    def GET_PARAMETER_NAMES(component):
        """
        Returns input component parameter names.
        """

        result = None

        parameter_controller = ParameterController.GET_CONTROLLER(component)

        result = parameter_controller.get_parameter_names()

        return result

    @staticmethod
    def GET_PARAMETER(component, name):
        """
        Get input component parameter which is registered with the input name.
        """

        result = None

        parameter_controller = ParameterController.GET_CONTROLLER(component)

        result = parameter_controller.get_parameter_names()

        return result


from pycoann.core import Annotation


class Parameter(Annotation):
    """
    Annotation which targets class method in order to bind it \
    with get/set parameter controller calls.
    """

    def __init__(self, name=None):

        self._super(Parameter).__init__()
        self.name = name
