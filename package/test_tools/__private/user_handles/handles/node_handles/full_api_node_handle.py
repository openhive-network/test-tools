from __future__ import annotations

from typing import TYPE_CHECKING

from test_tools.__private.full_api_node import FullApiNode
from test_tools.__private.user_handles.handles.node_handles.runnable_node_handle import RunnableNodeHandle

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle as Network


class FullApiNodeHandle(RunnableNodeHandle):
    def __init__(self, network: Network | None = None) -> None:
        super().__init__(
            implementation=FullApiNode(
                network=network,
                handle=self,
            )
        )
