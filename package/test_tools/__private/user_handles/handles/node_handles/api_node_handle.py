from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from test_tools.__private.api_node import ApiNode
from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase

if TYPE_CHECKING:
    from test_tools.__private.network import Network
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle


class ApiNodeHandle(NodeHandleBase):
    def __init__(self, network: Optional[NetworkHandle] = None):
        network_implementation: Optional[Network] = get_implementation(network)  # type: ignore
        super().__init__(
            implementation=ApiNode(
                network=network_implementation,
                handle=self,
            )
        )
