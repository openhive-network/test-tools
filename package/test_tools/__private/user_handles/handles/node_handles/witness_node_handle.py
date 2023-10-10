from __future__ import annotations

from typing import TYPE_CHECKING

from test_tools.__private.user_handles.handles.node_handles.runnable_node_handle import RunnableNodeHandle
from test_tools.__private.witness_node import WitnessNode

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle as Network


class WitnessNodeHandle(RunnableNodeHandle):
    def __init__(self, *, witnesses: list[str] | None = None, network: Network | None = None) -> None:
        super().__init__(
            implementation=WitnessNode(
                witnesses=witnesses,
                network=network,
                handle=self,
            )
        )
