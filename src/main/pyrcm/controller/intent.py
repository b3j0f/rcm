from pyrcm.controller.core import Controller
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
        list of intents and the intercepted callee resource.

        When a intent intercepts this, it just has to call this \
        in order to follow interception mechanism.
        """

        def __init__(
            self,
            interface_name,
            callee_name,
            args,
            kwargs,
            intents,
            callee
        ):

            self.interface_name = interface_name
            self.callee_name = callee_name
            self.next = next
            self.args = args
            self.kwargs = kwargs
            self.intents = intents

        def __call__(self):
            """
            Call first intent with this such as argument \
            or the intercepted callee resource.
            """

            result = None

            if self.intents:
                intent = self.intents.pop()
                result = intent.intercepts(self)
            else:
                result = self.callee(*self.args, **self.kwargs)

            return result

    class _IntentMatching(object):
        """
        Dedicated to manage intent matching.
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
        self.matchings_per_intent = []

    def add_intent(
        self,
        intent,
        interface_name=None,
        callee_name=None,
        dynamic_matching=None
    ):
        """
        Add an intent with optional arguments.
        The intent will intercepts if:
        * input interface_name matches with called interface name,
        * input callee_name matches with called callee name,
        * input dynamic_matching matches the interface_call.
        """

        intent_matching = IntentController._IntentMatching(
            interface_name,
            callee_name,
            dynamic_matching)

        intent_matchings = self.matchings_per_intent.get(
            intent, None)

        if intent_matchings is None:
            intent_matchings = [intent_matching]
            self.matchings_per_intent[intent] = intent_matchings
        else:
            intent_matchings.append(intent_matching)

    def remove_intent(self, intent):
        """
        Remove an intent.
        """

        del self.matchings_per_intent[intent]

    def get_intent(self, interface_call):
        """
        """

        result = []
        for intent, matching in enumerate(self.matchings_per_intent):
            if matching.match(interface_call):
                result.append(intent)

        return result


class BasicIntent(object):
    """
    Dedicated to intercepts component interface calls.
    """

    def intercepts(interface_caller):
        """
        Intercept a call to an interface.
        """

        return interface_caller()

from pycoann.core import Annotation


class Intent(Annotation):
    """
    Dedicated to associate a business resource to a component intent.
    """

    def __init__(
        self, interface_call=None, callee_call=None, dynamic_matching=None
    ):
        self.interface_call = interface_call
        self.callee_call = callee_call
        self.dynamic_matching = dynamic_matching
