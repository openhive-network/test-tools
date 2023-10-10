from __future__ import annotations

from test_tools.__private.scope.scope_singleton import current_scope


class ScopedObject:
    def __init__(self) -> None:
        current_scope.register(self)

    def at_exit_from_scope(self) -> None:
        """Called when exiting from scope occurs. By default does nothing."""
