from __future__ import annotations

from typing import TYPE_CHECKING

from test_tools.__private.scope.context_definition import Context

if TYPE_CHECKING:
    from test_tools.__private.scope.scoped_object import ScopedObject


class Scope:
    def __init__(self, parent: Scope | None) -> None:
        self.scoped_objects: list[ScopedObject] = []
        self.context: Context = Context(parent=parent.context if parent is not None else None)

    def enter(self) -> None:
        """By default it does nothing, executed on scope entrance."""

    def register(self, scoped_object: ScopedObject) -> None:
        self.scoped_objects.append(scoped_object)

    def exit_from_scope(self) -> None:
        """Executed _always_ on scope exit."""
        for scoped_object in reversed(self.scoped_objects):
            scoped_object.at_exit_from_scope()
