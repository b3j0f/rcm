from pyrcm.controller import Controller
import re


class IntentController(Controller):
    """
    Component intent controller. Manages interception of \
    component interface calls.
    """

    NAME = '/intent-controller'

    class InterfaceCall(object):
        """
        Interface call for Interface call interception.

        Contains an interface_name, a callee_name, \
        called arguments (args and kwargs), \
        list of interceptors and the intercepted callee resource.

        When a interceptor intercepts this, it just has to call this \
        in order to follow interception mechanism.
        """

        def __init__(
            self,
            interface_name,
            callee_name,
            args,
            kwargs,
            interceptors,
            callee
        ):

            self.interface_name = interface_name
            self.callee_name = callee_name
            self.next = next
            self.args = args
            self.kwargs = kwargs
            self.interceptors = interceptors

        def __call__(self):
            """
            Call first interceptor with this such as argument \
            or the intercepted callee resource.
            """

            result = None

            if self.interceptors:
                interceptor = self.interceptors.pop()
                result = interceptor.intercepts(self)
            else:
                result = self.callee(*self.args, **self.kwargs)

            return result

    class _InterceptorMatching(object):
        """
        Dedicated to manage interceptor matching.
        Matching condition is a regex on interface_name, callee_name \
        and dynamic_matching execution.
        """

        def __init__(
            self,
            interface_name=None,
            callee_name=None,
            dynamic_matching=None
        ):

            self.interface_name = \
                re.compile(interface_name) if interface_name is not None \
                else None
            self.callee_name = \
                re.compile(callee_name) if callee_name is not None \
                else None
            self.dynamic_matching = dynamic_matching

        def matches(self, interface_call):
            """
            Check if interface_name and callee_name and dynamic_matching \
            match with input interface_call.
            """

            result = False

            if self.interface_name is not None:
                result = self.interface_name.match(
                    interface_call.interface_name)
                if not result:
                    return result

            if self.callee_name is not None:
                result = self.callee_name.match(interface_call.callee_name)
                if not result:
                    return result

            if self.condition is not None:
                result = self.condition(interface_call)

            return result

    def __init__(self, component):

        self.component = component
        self.matchings_per_interceptor = []

    def add_interceptor(
        self,
        interceptor,
        interface_name=None,
        callee_name=None,
        dynamic_matching=None
    ):
        """
        Add an interceptor with optional arguments.
        The interceptor will intercepts if:
        * input interface_name matches with called interface name,
        * input callee_name matches with called callee name,
        * input dynamic_matching matches the interface_call.
        """

        interceptor_matching = IntentController._InterceptorMatching(
            interface_name,
            callee_name,
            dynamic_matching)

        interceptor_matchings = self.matchings_per_interceptor.get(
            interceptor, None)

        if interceptor_matchings is None:
            interceptors_matchings = [interceptor_matching]
            self.matchings_per_interceptor[interceptor] = interceptor_matchings
        else:
            interceptors_matchings.append(interceptor_matching)

    def remove_interceptor(self, interceptor):
        """
        Remove an interceptor.
        """

        del self.matchings_per_interceptor[interceptor]

    def get_interceptors(self, interface_call):
        """
        """

        result = []
        for interceptor, matching in enumerate(self.matchings_per_interceptor):
            if matching.match(interface_call):
                result.append(interceptor)

        return result


class Interceptor(object):
    """
    Dedicated to intercepts component interface calls.
    """

    def intercepts(interface_caller):
        """
        Intercept a call to an interface.
        """

        return interface_caller()
