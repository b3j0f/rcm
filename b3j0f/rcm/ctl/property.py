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

Component properties are also components which are dedicated to specify
functional properties configured from the component model.

Such properties have a value and a type which describe their kind of value.

In a hierachical concern, a property value can be given by its bound
properties.

Related to those properties, a property controller allows to synchronize
property values with an ImplController thanks to Dependency Injection/Inversion
of Control mechanisms. The implementation is able to set component properties,
or to get property values as soon as they change (or at constructor
initialization).
"""

__all__ = [
    'PropertyController',  'Property',  # property controller and component
    'SetPropertyCtrl', 'GetProperty', 'SetProperty',  # property annotations
]

from b3j0f.aop import weave, unweave
from b3j0f.rcm.core import Component
from b3j0f.rcm.ctl.core import Controller
from b3j0f.rcm.ctl.annotation import (
    CtrlAnnotation, getter_name, setter_name, C2CtrlAnnotation
)
from b3j0f.rcm.ctl.impl import ImplController


class Property(Component):
    """Manage property distribution among components.

    A Property uses Property ports in order to get value from the component
    model.

    It uses :

        - a ``name`` attribute unique among other component properties.
        - a ``value`` attribute in order to keep in memory a local value.
        - a property type (``ptype``) in order to specify kind of value.
        - a boolean ``update`` attribute in order to automatically update value
            after bound to a new property.
    """

    class PropertyError(Exception):
        """Handle Property errors.
        """
        pass

    NAME = '_name'  #: name attribute name
    VALUE = '_value'  #: value attribute name
    PTYPE = '_ptype'  #: ptype attribute name
    UPDATE = 'update'  #: update attribute name

    def __init__(
        self, name, value=None, ptype=None, update=True, *args, **kwargs
    ):
        """
        :param str name: property name.
        :param value: property value.
        :param type ptype: property type.
        :param bool update: if True (default), auto-update value as bound
            properties change.
        """
        super(Property, self).__init__(*args, **kwargs)

        self.name = name
        self.update = update
        self.ptype = ptype
        self.value = value

    @property
    def name(self):
        """Get name.

        :return: self name.
        :rtype: str
        """

        return self._name

    @name.setter
    def name(self, value):
        """Change of name.

        :param str name: new name to use.
        :raises: Property.PropertyError if name is already used by another
            component property.
        """

        self._set_name(name=value)

    def _set_name(self, name):
        """Change of name.

        :param str name: new name to use.
        :raises: Property.PropertyError if name is already used by another
            component property.
        """

        # do something only if name != self name
        if name != self.name:
            for rport in self._rports:
                properties = Property.GET_PORTS(component=rport)
                for pname in properties:
                    prop = properties[pname]
                    if prop is not self and prop.name == name:
                        raise Property.PropertyError(
                            'Name {0} already used by {1}'.format(
                                name, prop
                            )
                        )
            # if name is unique, use it
            self._name = name

    @property
    def value(self):
        """Get self value.
        """

        return self._get_value()

    def _get_value(self):
        """Get value related to self._value or from bound Properties if None.

        :return: self value from self._value or from bound Proprties if None.
        """

        result = self._value  # default is self._value

        if result is None:  # if result is None, search among self properties
            properties = Property.GET_PORTS(component=self)  # bound properties
            ptype = self.ptype  # store self ptype for dynamic reasons
            for name in properties:
                prop = properties[name]
                value = prop.value  # get bound property value
                if value is not None and (
                    ptype is None or isinstance(value, ptype)
                ):  # udpate value as soon as a compatible value is found
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
        else:
            # update property controller properties
            pc = PropertyController.get_nf(component=component)
            if pc is not None:
                try:
                    value = self.value
                except Property.PropertyError:
                    pass
                else:
                    pc.properties[self.name] = value

    def _on_unbind(self, component, *args, **kwargs):

        super(Property, self)._on_unbind(component=component, *args, **kwargs)

        # update property controller properties
        pc = PropertyController.get_nf(component=component)
        if pc is not None:
            pc._update_properties()

    def propagate_value(self, prop=None, force=False, error=True):
        """Propagate value on all bound properties and property controller.

        :param Property prop: property to update. If None, update all
            reverted properties.
        :param bool force: force to update reverted properties whatever value
            of update.
        :raises: Property.PropertyError if self and prop types do not match
            and error (False by default).
        """

        value = self.value  # get self value
        # if prop is None, propagate on all reverted properties
        if prop is None:
            for rport in self._rports:
                if isinstance(rport, Property) and (force or rport.update):
                    try:
                        rport.value = value  # try to change of value
                    except Property.PropertyError:
                        if error:  # raise the exception if error
                            raise
                else:  # update property controller with self value
                    pc = PropertyController.get_nf(rport)
                    if pc is not None:
                        pc.properties[self.name] = value
        elif force or prop.update:
            try:
                prop.value = value  # try to change of value
            except Property.PropertyError:
                if error:  # raise the exception if error
                    raise


class PropertyController(Controller):
    """Dedicated to manage component properties.

    The local dict ``properties`` is synchronized with component property
    values.
    """

    PROPERTIES = 'properties'  #: local dict of properties by name

    def __init__(self, *args, **kwargs):

        super(PropertyController, self).__init__(*args, **kwargs)
        # initialiaze self properties
        self.properties = {}

    def _update_properties(self):
        """Update properties from component properties.
        """

        self.properties = {}  #: initialize this properties

        for rport in self._rports:
            properties = Property.GET_PORTS(component=rport)
            for name in properties:
                prop = properties[name]
                try:
                    value = prop.value
                except Property.PropertyError:
                    pass
                else:
                    self.properties[name] = value

    def _enrich_impl_cons_params(self, jp, *args, **kwargs):
        """Enrich component implementation constructor params with self
        properties.

        :param Joinpoint jp: component implementation constructor joinpoint.
        :param list args: component implementation constructor varargs.
        :param dict kwargs: component implementation constructor keywords.
        """

        # enrich joinpoint params
        params = jp.kwargs
        ic = jp.kwargs['self'] if 'self' in jp.kwargs else jp.args[0]

        self_properties = self.properties  # get self properties

        # enrich with dynamic properties
        for name in self_properties:
            if name not in params:
                value = self_properties[name]
                params[name] = value

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

        result = jp.proceed()  # execute the constructor

        return result

    def _on_bind(self, component, *args, **kwargs):

        super(PropertyController, self)._on_bind(
            component=component, *args, **kwargs
        )

        # update self properties from component properties
        self._update_properties()

        # weave _enrich_impl_cons_params on IC instantiate method
        ic = ImplController.get_controller(component=component)
        if ic is not None:
            weave(
                target=ic.instantiate, ctx=ic,
                advices=self._enrich_impl_cons_params
            )

    def _on_unbind(self, component, *args, **kwargs):

        super(PropertyController, self)._on_unbind(
            component=component, *args, **kwargs
        )

        # update self properties from component properties
        self._update_properties()

        # unweave _enrich_impl_cons_params on IC instantiate method
        ic = ImplController.get_controller(component=component)
        if ic is not None:
            unweave(
                target=ic.instantiate, ctx=ic,
                advices=self._enrich_impl_cons_params
            )


class SetPropertyCtrl(C2CtrlAnnotation):
    """Inject a PropertyController in a component implementation.
    """

    def get_value(self, component, *args, **kwargs):

        return PropertyController.get_controller(component)


class _PropertyAnnotation(CtrlAnnotation):
    """Base annotation for DI/IoC of property with component implementation.
    """
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
