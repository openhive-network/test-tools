from __future__ import annotations

from typing import TYPE_CHECKING

from test_tools.__private.preconfigured_node import PreconfiguredNode

if TYPE_CHECKING:
    from test_tools.__private.network import Network
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class HafNode(PreconfiguredNode):
    def __init__(
        self, *, name: str = "HafNode", network: Network | None = None, handle: NodeHandle | None = None
    ) -> None:
        super().__init__(name=name, network=network, handle=handle)

        self.config.plugin.append('sql_serializer')
