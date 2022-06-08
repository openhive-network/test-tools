from __future__ import annotations

from typing import overload, TYPE_CHECKING

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handle import Handle
    from test_tools.__private.user_handles.implementation import Implementation


@overload
def get_implementation(handle: None) -> None:
    ...


@overload
def get_implementation(handle: Handle) -> Implementation:
    ...


def get_implementation(handle):
    if handle is None:
        return None

    return handle._Handle__implementation  # pylint: disable=protected-access


@overload
def get_handle(implementation: None) -> None:
    ...


@overload
def get_handle(implementation: Implementation) -> Handle:
    ...


def get_handle(implementation):
    if implementation is None:
        return None

    return implementation._Implementation__handle  # pylint: disable=protected-access
