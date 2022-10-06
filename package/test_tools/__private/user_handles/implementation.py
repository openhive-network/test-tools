from __future__ import annotations

from abc import ABC
from typing import Generic, Optional, TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handle import Handle


class Implementation(ABC):
    """Base class for all objects pointed by handles. Contains handle by which is pointed."""

    def __init__(self, *args, handle: Optional[Handle], **kwargs):
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self.__handle = handle  # pylint: disable=unused-private-member; It is used in `user_handles.get_handle`.
