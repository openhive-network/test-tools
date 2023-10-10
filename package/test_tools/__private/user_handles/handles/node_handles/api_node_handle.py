from __future__ import annotations

from typing import TYPE_CHECKING

from test_tools.__private.api_node import ApiNode
from test_tools.__private.user_handles.handles.node_handles.runnable_node_handle import RunnableNodeHandle

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle as Network


class ApiNodeHandle(RunnableNodeHandle):
    def __init__(self, network: Network | None = None) -> None:
        super().__init__(
            implementation=ApiNode(
                network=network,
                handle=self,
            )
        )
