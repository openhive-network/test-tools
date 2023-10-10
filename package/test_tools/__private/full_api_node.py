from __future__ import annotations

from typing import TYPE_CHECKING

from test_tools.__private.api_node import ApiNode

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle as Network
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class FullApiNode(ApiNode):
    def __init__(
        self, *, name: str = "FullApiNode", network: Network | None = None, handle: NodeHandle | None = None
    ) -> None:
        super().__init__(name=name, network=network, handle=handle)
        self._enable_api_plugins(plugins=["account_history_api"])
