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
    'PropertyController',  'Property',  # property controller and component
    'SetPropertyCtrl', 'GetProperty', 'SetProperty',  # property annotations
]

from b3j0f.aop import weave, unweave
from b3j0f.rcm.core import Component
from b3j0f.rcm.ctrl.core import Controller
from b3j0f.rcm.ctrl.annotation import (
    CtrlAnnotation, getter_name, setter_name, C2CtrlAnnotation
)
from b3j0f.rcm.ctrl.impl import ImplController


class PropertyController(Controller):
    """Dedicated to manage component parameters.
    """

    @property
    def properties(self):
        """Get properties.
        """

        return Property.GET_PORTS(component=self)

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
                params[name] = prop.value

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
        except AttributeError:  # do nothing if constructor does not exist
            pass
        else:
            gps = GetProperty.get_annotations(constructor)
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

        # update values from component properties
        properties = Property.GET_PORTS(component=component)
        for name in properties:
            prop = properties[name]
            self.properties[name] = prop.value

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


class Property(Component):
    """Manage property distribution among components.

    A Property uses Property ports in order to get value from the component
    model.

    It uses :

        - a ``value`` attribute in order to keep in memory a local value.
        - a property type (``ptype``) in order to specify kind of value.
        - a boolean ``update`` attribute in order to automatically update value
            after bound to a new property.
    """

    class PropertyError(Exception):
        """Handle Property errors.
        """
        pass

    VALUE = '_value'
    PTYPE = '_ptype'

    def __init__(self, value=None, ptype=None, update=True, *args, **kwargs):
        """
        :param value: property value.
        :param type ptype: property type.
        :param bool update: if True (default), auto-update value as bound
            properties change.
        """
        super(Property, self).__init__(*args, **kwargs)

        self.update = update
        self.ptype = ptype
        self.value = value

    @property
    def value(self):
        """Get self value.
        """

        return self._get_value()

    def _get_value(self):

        result = None

        ptype = self.ptype

        if result is None:  # if result is None, search among self properties
            properties = Property.GET_PORTS(self)
            for name in properties:
                prop = properties[name]
                value = prop.value
                if (
                    value is not None and (
                        ptype is None or isinstance(value, ptype)
                    )
                ):
                    # stop search when value is compatible with ptype
                    result = value
                    break

        return result

    @value.setter
    def value(self, value):
        """Change of value.

        :param value: new value to use.
        :raises: PropertyError if ptype is not None and value does not inherit
            from ptype.
        """

        self._set_value(value)

    def _set_value(self, value):
        """Change of value.

        :param value: new value to use.
        :raises: PropertyError if ptype is not None and value does not inherit
            from ptype.
        """

        # nonify value if value is None or ptype is None
        if value is None or self.ptype is None:
            self._value = value
        elif isinstance(value, self.ptype):  # check type
                self._value = value
        else:  # otherwise, raise an error
            raise Property.PropertyError(
                'Wrong property type {0} with {1}'.format(
                    self.ptype, value
                )
            )
        # try to update reversed properties
        self.propagate_value(error=False)

    @property
    def ptype(self):
        """Get ptype.

        :return: ptype.
        :rtype: type
        """

        return self._ptype

    @ptype.setter
    def ptype(self, value):
        """Change of ptype.

        :param type value: new ptype to use.
        """

        self._set_ptype(ptype=value)

    def _set_ptype(self, ptype):
        """Change of ptype.

        :param type value: new ptype to use.
        """

        value = self.value
        # change of value if value is None, or ptype is None or
        # value is an instance of ptype
        if value is None or ptype is None or isinstance(value, ptype):
            self._ptype = ptype
        else:  # otherwise, raise an error
            raise Property.PropertyError(
                'Wrong ptype {0} with existing value {1}'.format(ptype, value)
            )

    def _on_bind(self, component, *args, **kwargs):

        super(Property, self)._on_bind(component=component, *args, **kwargs)

        # propagate value if component is a newly bound Property
        if isinstance(component, Property):
            self.propagate_value(prop=component, force=False, error=False)

    def propagate_value(self, prop=None, force=False, error=True):
        """Propagate value on all bound properties.

        :param Property prop: property to update. If None, update all
            reverted properties.
        :param bool force: force to update reverted properties whatever value
            of update.
        :raises: Property.PropertyError if self and prop types do not match
            and error (False by default).
        """

        value = self.value
        # if prop is None, propagate on all reverted properties
        if prop is None:
            for rport in self._rports:
                if isinstance(rport, Property) and (force or rport.update):
                    try:
                        rport.value = value  # try to change of value
                    except Property.PropertyError:
                        if error:  # raise the exception if error
                            raise
        elif force or prop.update:
            try:
                prop.value = value  # try to change of value
            except Property.PropertyError:
                if error:  # raise the exception if error
                    raise
