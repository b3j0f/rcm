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

"""Module dedicated to bind properties to components.
"""

__all__ = [
    'PropertyController',  # property controller
    'SetPropertyCtrl', 'GetProperty', 'SetProperty',  # property annotations
]

from b3j0f.aop import weave, unweave
from b3j0f.rcm.ctrl.core import Controller
from b3j0f.rcm.ctrl.annotation import (
    CtrlAnnotation, gettername, settername, C2CtrlAnnotation
)
from b3j0f.rcm.ctrl.impl import ImplController


class PropertyController(Controller):
    """Dedicated to manage component parameters.
    """

    PROPERTIES = 'properties'  #: properties field name

    def __init__(self, properties=None, *args, **kwargs):

        super(PropertyController, self).__init__(*args, **kwargs)
        self.properties = {} if properties is None else properties

    def enrich_instantiation_params(self, jp, *args, **kwargs):
        """Enrich instantiation params with self properties.
        """

        # enrich joinpoint params
        params = jp.kwargs['params']
        ic = jp.kwargs['self'] if 'self' in jp.kwargs else jp.args[0]

        # enrich with dynamic properties
        for name in self.properties:
            if name not in params:
                prop = self.properties[name]
                params[name] = prop

        # enrich with GetProperty annotations from cls
        gps = GetProperty.get_annotations(ic.cls)
        for gp in gps:
                param = gp.name if gp.param is None else gp.param
                if param not in params:
                    params[param] = gps.params[gp.name]
        # and from the constructor
        try:
            constructor = getattr(
                self._cls, '__init__', getattr(
                    self._cls, '__new__'
                )
            )
        except AttributeError:
            pass
        else:
            gps = GetProperty.get_annotations(
                constructor
            )
            for gp in gps:
                param = gp.name if gp.param is None else gp.param
                if param not in params:
                    params[param] = gps.params[gp.name]

        result = jp.proceed()

        return result

    def _on_bind(self, component, *args, **kwargs):

        super(PropertyController, self)._on_bind(
            component=component, *args, **kwargs
        )

        # weave enrich_instantiation_params on IC instantiate method
        ic = ImplController.get_controller(component=component)
        if ic is not None:
            weave(
                target=ic.instantiate, ctx=ic,
                advices=self.enrich_instantiation_params
            )

    def _on_unbind(self, component, *args, **kwargs):

        super(PropertyController, self)._on_unbind(
            component=component, *args, **kwargs
        )

        # unweave enrich_instantiation_params on IC instantiate method
        ic = ImplController.get_controller(component=component)
        if ic is not None:
            unweave(
                target=ic.instantiate, ctx=ic,
                advices=self.enrich_instantiation_params
            )


class SetPropertyCtrl(C2CtrlAnnotation):
    """Inject a PropertyController in an implementation.
    """

    def get_value(self, component, *args, **kwargs):

        return PropertyController.get_controller(component)


class _PropertyAnnotation(CtrlAnnotation):

    NAME = 'name'  #: name field name

    __slots__ = (NAME, ) + CtrlAnnotation.__slots__

    def __init__(self, name, *args, **kwargs):

        super(_PropertyAnnotation, self).__init__(*args, **kwargs)

        self.name = name


class SetProperty(_PropertyAnnotation):
    """Set a property value from an implementation attr.
    """

    __slots__ = _PropertyAnnotation.__slots__

    def get_resource(self, component, attr, *args, **kwargs):

        pc = PropertyController.get_controller(component=component)

        if pc is not None:
            # get the right name
            name = setter_name(attr) if self.name is None else self.name
            # and the right property
            result = pc.properties[name]

        return result


class GetProperty(_PropertyAnnotation):
    """Get a property value from an implementation attr.
    """

    __slots__ = _PropertyAnnotation.__slots__

    def apply_on(self, component, attr, *args, **kwargs):

        pc = PropertyController.get_controller(component=component)

        if pc is not None:
            # get attr result
            value = attr()
            # get the right name
            name = getter_name(attr) if self.name is None else self.name
            # udate property controller
            pc.properties[name] = value
