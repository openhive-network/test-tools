from __future__ import annotations

from typing import TypeVar

from test_tools.__private.user_handles.handle import Handle
from test_tools.__private.user_handles.implementation import Implementation

T = TypeVar("T")
P = TypeVar("P")


def get_private_member(_: type[T], owner_class: type[P], owner: P, attribute_name: str) -> T:
    owner_class_name = owner_class.__name__.split("[")[0]
    full_member_name = f"_{owner_class_name}{attribute_name}"
    return getattr(owner, full_member_name)  # type: ignore[no-any-return]


def get_implementation(handle: Handle, expected_type: type[T]) -> T:
    return get_private_member(expected_type, Handle, handle, "__implementation")


def get_handle(implementation: Implementation, expected_type: type[T]) -> T:
    return get_private_member(expected_type, Implementation, implementation, "__handle")
