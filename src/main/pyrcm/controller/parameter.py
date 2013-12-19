from pyrcm.controller import Controller


class ParameterController(Controller):
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


from pycoann.core import Decorator
from pycoann.call import Target


@Target(Target.FUNC)
class Parameter(Decorator):
    """
    Decorator which targets class method in order to bind it \
    with get/set parameter controller calls.
    """

    def __init__(self, name=None):

        self._super(Parameter).__init__()
        self.name = name
