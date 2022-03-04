from test_tools import clean_up_policy
from test_tools.constants import CleanUpPolicy
from test_tools.private.scope.scoped_object import ScopedObject


class ScopedCleanUpPolicy(ScopedObject):
    """
    Scoped object which:
    - on creation -- stores previous clean up policy and sets its own
    - at exit from scope -- restores previous clean up policy
    """

    def __init__(self, policy: CleanUpPolicy):
        super().__init__()

        self.previous_policy = clean_up_policy.get_default()
        clean_up_policy.set_default(policy)

    def at_exit_from_scope(self):
        clean_up_policy.set_default(self.previous_policy)
