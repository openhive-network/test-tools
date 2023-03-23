from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from test_tools.__private.api_node import ApiNode

if TYPE_CHECKING:
    from test_tools.__private.network import Network
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class FullApiNode(ApiNode):
    def __init__(
        self, *, name: str = "FullApiNode", network: Optional[Network] = None, handle: Optional[NodeHandle] = None
    ):
        super().__init__(name=name, network=network, handle=handle)
        self._enable_api_plugins(plugins=["account_history_api"])
