from __future__ import annotations

from typing import TYPE_CHECKING

from test_tools.__private import cleanup_policy
from test_tools.__private.scope.scoped_object import ScopedObject

if TYPE_CHECKING:
    from test_tools.__private.constants import CleanupPolicy


class ScopedCleanupPolicy(ScopedObject):
    """
    Scoped object which.

        - on creation -- stores previous cleanup policy and sets its own
        - at exit from scope -- restores previous cleanup policy.
    """

    def __init__(self, policy: CleanupPolicy) -> None:
        super().__init__()

        self.previous_policy = cleanup_policy.get_default()
        cleanup_policy.set_default(policy)

    def at_exit_from_scope(self) -> None:
        cleanup_policy.set_default(self.previous_policy)
