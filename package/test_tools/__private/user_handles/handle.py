from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test_tools.__private.user_handles.implementation import Implementation


class Handle:
    """Base class for all objects pointed by handles. Contains handle by which is pointed."""

    def __init__(self, *args, implementation: Implementation, **kwargs):
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self.__implementation: Implementation = implementation  # pylint: disable=unused-private-member
        # unused-private-member is disabled, because __implementation is used in `user_handles.get_implementation`.

    def __str__(self) -> str:
        return str(self.__implementation)

    def __repr__(self) -> str:
        return repr(self.__implementation)
