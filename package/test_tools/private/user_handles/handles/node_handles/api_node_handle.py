from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from test_tools.private.api_node import ApiNode
from test_tools.private.user_handles.get_implementation import get_implementation
from test_tools.private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase

if TYPE_CHECKING:
    from test_tools.private.user_handles.handles.network_handle import NetworkHandle as Network


class ApiNodeHandle(NodeHandleBase):
    def __init__(self, network: Optional[Network] = None):
        super().__init__(
            implementation=ApiNode(
                network=get_implementation(network),
                handle=self,
            )
        )
