from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handle import Handle
    from test_tools.__private.user_handles.implementation import Implementation


def get_implementation(handle: Optional[Handle]) -> Optional[Implementation]:
    if handle is None:
        return None

    return handle._Handle__implementation  # pylint: disable=protected-access


def get_handle(implementation: Optional[Implementation]) -> Optional[Handle]:
    if implementation is None:
        return None

    return implementation._Implementation__handle  # pylint: disable=protected-access
