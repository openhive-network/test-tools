from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test_tools.__private.user_handles.implementation import Implementation


class Handle:
    """Base class for all objects pointed by handles. Contains handle by which is pointed."""

    def __init__(self, *args, implementation: Implementation, **kwargs):
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self.__implementation = implementation

    def __str__(self) -> str:
        return str(self.__implementation)

    def __repr__(self) -> str:
        return repr(self.__implementation)
