from __future__ import annotations

from typing import cast, Optional, TYPE_CHECKING

from test_tools.__private.haf_node import HafNode
from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle as Network


class HafNodeHandle(NodeHandleBase):
    def __init__(self, network: Optional[Network] = None) -> None:
        super().__init__(
            implementation=HafNode(
                network=get_implementation(network),
                handle=self,
            )
        )

    @property
    def __implementation(self) -> HafNode:
        return cast(HafNode, get_implementation(self))

    @property
    def session(self) -> Session:
        """Returns Sqlalchemy database session"""
        return self.__implementation.session
