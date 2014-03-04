"""
Contains Component definition.
"""
from uuid import uuid1 as uuid
import inspect
import types


class Component(dict):
    """
    Component which contains Interfaces and a business implementation.
    """

    class NoSuchInterfaceError(Exception):
        """
        Exception dedicated to component missing interface.
        """

        def __init__(self, component, name=None, component_type=None):
            message =\
                Component.NoSuchInterfaceError._GET_MESSAGE(
                    component, name, component_type)
            super(Component.NoSuchInterfaceError, self).__init__(message)

        @staticmethod
        def _GET_MESSAGE(component, name, component_type):
            """
            Get default message for missing interface name in component.
            """

            postfix = \
                "named {0}".format(name) if name is not None \
                else "of type {0}".format(component_type)
            result = "{0} has no interface {1}".format(component, postfix)

            return result

    NAME = 'component'

    IMPLEMENTATION = 'implementation'

    def __init__(
        self, *interfaces, **named_interfaces
    ):
        """
        Constructor which register interfaces with generated name \
and named interfaces.
        """

        self.interfaces = dict()

        # register interface with a generated name.
        for interface in interfaces:
            self.set_interface(interface=interface)

        # register interfaces
        for name, interface in named_interfaces.iteritems():
            self.set_interface(name=name, interface=interface)

    def __delitem__(self, key):
        result = self.remove_interface(name=key)
        return result

    def __getitem__(self, key):
        result = self.get_interface(name=key)
        return result

    def __setitem__(self, key, value):
        result = self[key] if key in self else None
        self.set_interface(name=key, interface=value)
        return result

    def renew_implementation(self, implementation_type, **parameters):
        """
        Instantiate business element and returns it.
        The instantiation is done with parameters and references of this \
component.
        """

        result = implementation_type(**parameters)

        self.set_implementation(result)

        return result

    def get_implementation(self):
        """
        Get component implementation.
        """

        return getattr(self, Component.IMPLEMENTATION, self)

    def set_implementation(self, implementation):
        """
        Set component implementation.
        """

        result = getattr(self, Component.IMPLEMENTATION, None)

        if result is not implementation:
            setattr(self, Component.IMPLEMENTATION, implementation)

            if implementation is not None:

                ComponentAnnotation.apply_on_implementation(
                    self, result, implementation)

                self.update_implementation(result, implementation)

        return result

    def update_implementation(self, old, new):
        """
        Called when this component change of implementation.
        """

        if old is new:
            return

        def apply_on_public_methods(implementation, func):
            """
            Apply input func on all implementation public methods.
            Func takes in the business component and the method in parameters.
            """

            field_names = dir(implementation)

            for field_name in field_names:
                field = getattr(implementation, field_name)

                if inspect.ismethod(field) and field_name[0] != '_':
                    func(self, field)

        # remove old implementation public methods from business component
        if old is not self and old is not None:
            apply_on_public_methods(
                old, lambda c, f: delattr(c, f.__name__))

        # add new implementation public methods to business component
        if new is not self and new is not None:
            apply_on_public_methods(
                new, lambda c, f: setattr(c, f.__name__, f))

    def get_interface(self, name=None, interface_type=None, error=True):
        """
        Get interface registered with the input name or the first which
        inherits from input interface_type.
        If error is True, raises NoSuchInterfaceError if interface name or interface_type
        does not exist. Else returns None.
        """

        result = None

        if name is None:
            for interface in self.values():
                if isinstance(interface, interface_type):
                    result = interface
                    break
            if result is None and error:
                raise Component.NoSuchInterfaceError(
                    self,
                    component_type=interface_type)

        elif name not in self and error:
            raise Component.NoSuchInterfaceError(self, name=name)

        else:
            try:
                result = super(Component, self).__getitem__(name)
            except KeyError:
                pass

        return result

    def get_interfaces(
        self, interface_types=(object,)
    ):
        """
        Get a set of couple (interface name, interface).
        interface_types is a type or a tuple of types.
        include_controllers permits to include controllers if True
        (False by default).
        """

        result = dict()

        if not isinstance(interface_types, tuple):
            interface_types = (interface_types,)

        for name, interface in self.iteritems():
            if isinstance(interface, interface_types):
                result[name] = interface

        return result

    def get_interface_names(self, interface):
        """
        Get input component interface name.
        Raises NoSuchInterfaceError if interface does not exists.
        """

        result = []

        for interface_name, component_interface in self.iteritems():
            if component_interface is interface:
                result.append(interface_name)

        return result

    def has_interface(self, name):
        """
        Check if interface exists in this component.
        """

        result = name in self

        return result

    def set_interface(self, interface, name=None):
        """
        Set an interface with input name, and returns \
previous interface registered with the same name if replace is False \
else generate a new name for the new interface.
        """

        result = self.get(name, None)

        if name is None:
            name = Component.GENERATE_INTERFACE_NAME(interface, generated=True)

        super(Component, self).__setitem__(name, interface)

        self.on_set_interface(name, result, interface)

        return result

    def on_set_interface(self, name, old, new):
        """
        Called after setting an interface.
        """
        pass

    def remove_interface(
        self, name=None, interface=None, interface_type=types.NoneType, error=True
    ):
        """
        Remove an interface from this component and returns it. \
        If error, raises a NoSuchInterfaceError in case of name does not exist.
        """

        result = None

        if name is None:
            for interface_name, _interface in self.iteritems():
                if _interface is interface or \
                        isinstance(_interface, interface_type):
                    name = interface_name
                    break

        if name is not None:

            if name not in self and error:
                raise Component.NoSuchInterfaceError(self, name=name)

            result = super(Component, self).__getitem__(name)

            super(Component, self).__delitem__(name)

            self.on_remove_interface(name, result)

        return result

    def on_remove_interface(self, name, interface):
        """
        Called after removing an interface.
        """
        pass

    @staticmethod
    def GENERATE_INTERFACE_NAME(interface, generated=False):
        """
        Generate interface name.
        """

        result = ""

        interface_type = type(interface) if not inspect.isclass(interface) \
            else interface

        result = "{0}.{1}".format(
            getattr(interface_type, '__module__'),
            getattr(interface_type, '__name__'))

        if generated:
            result += "_{0}".format(uuid())

        return result

from pycoann.core import Annotation


class ComponentAnnotation(Annotation):
    """
    Annotation dedicated to enrich business with component properties.
    """

    __PARAM_NAMES_WITH_INDEX__ = dict()

    def _push_param(self, name, param, argspec, kwargs):
        """
        Fill input kwargs with param value and name.
        If name is None, a default param index is got from self
        __PARAM_NAMES_WITH_INDEX__ static dictionary in order to
        find the right position in argspec.args arguments.
        """

        self_param = getattr(self, name, None)

        kwargs_index = None

        if self_param is not None:
            if self_param in argspec.args or argspec.keywords is not None:
                kwargs_index = self_param
        else:
            index = type(self).__PARAM_NAMES_WITH_INDEX__.get(name)
            if len(argspec.args) > index:
                kwargs_index = argspec.args[index]

        if kwargs_index is not None:
            kwargs[kwargs_index] = param

    def apply_on(self, component, old_impl, new_impl):
        """
        Apply self annotation to input implementation
        in the context of input component.
        """

        pass

    @classmethod
    def apply_on_implementation(
        component_annotation_type, component, old_impl, new_impl
    ):
        """
        Static method which is called
        when a component implementation is renewed.
        """

        annotations = component_annotation_type.get_annotations(new_impl)

        for annotation in annotations:
            annotation.apply_on(component, old_impl, new_impl)

        field_names = dir(new_impl)

        for field_name in field_names:
            new_field = getattr(new_impl, field_name, None)
            old_field = getattr(old_impl, field_name, None)
            annotations = component_annotation_type.get_annotations(new_field)
            for annotation in annotations:
                annotation.apply_on(component, old_field, new_field)

from pycoann.core import AnnotationWithoutParameters


class ComponentAnnotationWithoutParameters(
    AnnotationWithoutParameters, ComponentAnnotation
):
    """
    AnnotationWithoutParameters dedicated to enrich implementation
    with component properties.
    """

    pass


class Context(ComponentAnnotationWithoutParameters):
    """
    Used to inject a context component in a component implementation.
    """

    def apply_on(self, component, old_impl, new_impl):
        new_impl(component)
