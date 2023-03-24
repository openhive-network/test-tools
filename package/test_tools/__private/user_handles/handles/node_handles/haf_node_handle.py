from __future__ import annotations

from typing import cast, Optional, TYPE_CHECKING

from test_tools.__private.haf_node import HafNode
from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle as Network


class HafNodeHandle(NodeHandleBase):
    def __init__(self, network: Optional[Network] = None, database_url: str = HafNode.DEFAULT_DATABASE_URL) -> None:
        super().__init__(
            implementation=HafNode(
                network=get_implementation(network),
                database_url=database_url,
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

    @property
    def database_url(self) -> str:
        """Returns haf database url"""
        return self.__implementation.database_url
