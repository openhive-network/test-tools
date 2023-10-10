from __future__ import annotations

from typing import TYPE_CHECKING

from test_tools.__private.raw_node import RawNode
from test_tools.__private.user_handles.handles.node_handles.runnable_node_handle import RunnableNodeHandle

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle as Network


class RawNodeHandle(RunnableNodeHandle):
    def __init__(self, network: Network | None = None) -> None:
        super().__init__(
            implementation=RawNode(
                network=network,
                handle=self,
            )
        )
