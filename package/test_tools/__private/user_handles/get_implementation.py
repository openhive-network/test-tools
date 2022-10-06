from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from test_tools.__private.type_annotations.handle_implementations import UserHandleImplementation

if TYPE_CHECKING:
    from typing import Optional

    from test_tools.__private.user_handles.handle import Handle

T = TypeVar("T")


def get_implementation(handle: Handle) -> Optional[UserHandleImplementation]:
    if handle is None:
        return None

    return handle._implementation  # pylint: disable=protected-access


def get_handle(implementation: UserHandleImplementation) -> Optional[Handle]:
    if implementation is None:
        return None

    return implementation.__handle  # pylint: disable=protected-access
