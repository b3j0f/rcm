from pyrcm.controller import Controller


class ParameterController(Controller):
    """
    Dedicated to manage component parameters.
    """

    def __init__(self, component, **kwargs):
        super(ParameterController, self).__init__(component=component)
        self._params = kwargs.copy()

    def get_params(self):
        """
        Returns component parameters.
        """

        return self._params

    def GET_PARAMS(component):
        """
        Returns input component parameters.
        """

        result = None

        parameter_controller = ParameterController.GET_CONTROLLER(component)

        if parameter_controller is not None:
            result = parameter_controller.get_params()

        return result
