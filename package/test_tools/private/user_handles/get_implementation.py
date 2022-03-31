from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from test_tools.private.user_handles.implementation import Implementation


def get_implementation(handle: Optional[Any]) -> Optional[Implementation]:
    if handle is None:
        return None

    return handle._Handle__implementation  # pylint: disable=protected-access


def get_handle(implementation: Optional[Implementation]) -> Optional[Any]:
    if implementation is None:
        return None

    return implementation._Implementation__handle  # pylint: disable=protected-access
