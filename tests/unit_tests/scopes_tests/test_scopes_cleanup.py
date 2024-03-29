from __future__ import annotations

from typing import TYPE_CHECKING

from test_tools.__private.scope import ScopedObject, current_scope

if TYPE_CHECKING:
    from collections.abc import Iterable


class ScopedObjectMock(ScopedObject):
    def __init__(self) -> None:
        super().__init__()
        self.at_exit_from_scope_was_called = False

    def at_exit_from_scope(self) -> None:
        self.at_exit_from_scope_was_called = True


def test_objects_cleanup_in_single_scope() -> None:
    object_outside = ScopedObjectMock()

    with current_scope.create_new_scope("test-scope"):
        object_inside = ScopedObjectMock()
        expected_state(live=[object_outside, object_inside])

    expected_state(live=[object_outside], dead=[object_inside])


def test_objects_cleanup_in_multiple_scopes() -> None:
    object_outside = ScopedObjectMock()

    with current_scope.create_new_scope("first"):
        object_in_first = ScopedObjectMock()

        with current_scope.create_new_scope("second"):
            object_in_second = ScopedObjectMock()
            expected_state(live=[object_outside, object_in_first, object_in_second])

        expected_state(live=[object_outside, object_in_first], dead=[object_in_second])

    expected_state(live=[object_outside], dead=[object_in_first, object_in_second])


def expected_state(*, live: Iterable[ScopedObjectMock] = (), dead: Iterable[ScopedObjectMock] = ()) -> None:
    assert all(not scoped_object.at_exit_from_scope_was_called for scoped_object in live)
    assert all(scoped_object.at_exit_from_scope_was_called for scoped_object in dead)
