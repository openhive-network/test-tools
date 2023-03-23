from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from test_tools.__private.full_api_node import FullApiNode
from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle as Network


class FullApiNodeHandle(NodeHandleBase):
    def __init__(self, network: Optional[Network] = None):
        super().__init__(
            implementation=FullApiNode(
                network=get_implementation(network),
                handle=self,
            )
        )
