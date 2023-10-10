from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handle import Handle


class Implementation:
    """Base class for all objects pointed by handles. Contains handle by which is pointed."""

    def __init__(self, *args: Any, handle: Handle | None, **kwargs: Any) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self.__handle = handle
