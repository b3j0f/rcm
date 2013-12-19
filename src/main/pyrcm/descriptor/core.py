from pyrcm.core import Component


@Component
class DescriptorManager(object):
    """
    Dedicated to manage descriptors.
    """

    pass


class Descriptor(object):
    """
    Dedicated to get a component description or get a component from a \
    description.
    """

    def get_description(self, component):
        """
        Get a description from input component.
        """

        raise NotImplementedError()

    def get_component(self, description):
        """
        Get a component from a description.
        """

        raise NotImplementedError()
