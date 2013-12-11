from pyrcm.controller import Controller
from pyrcm.controller.parameter import ParameterController


class Business(Controller):
    """
    Dedicated to manage comopnent business.
    """

    def renew_implementation(self, implementation_type):

        parameters = dict()
        parameterController = \
            ParameterController.GET_CONTROLLER(self.component)

        for name in parameterController.get_parameter_names():
            parameter = parameterController.get_parameter(name)
            parameters[name] = parameter

        for name, interface in self.component:
            if isinstance(interface, Interface):
                

        result = implementation_type(**parameters)

        self.set_implementation(result)

        return result

    def get_implementation(self):
        """
        Get component implementation.
        """

        return self.implementation

    def set_implementation(self, implementation):
        """
        Set component implementation.
        """

        self.implementation = implementation
