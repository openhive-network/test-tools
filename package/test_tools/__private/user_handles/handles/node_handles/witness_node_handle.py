from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase
from test_tools.__private.witness_node import WitnessNode

if TYPE_CHECKING:
    from test_tools.__private.network import Network
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle


class WitnessNodeHandle(NodeHandleBase):
    def __init__(self, *, witnesses: Optional[List[str]] = None, network: Optional[NetworkHandle] = None):
        network_implementation: Optional[Network] = get_implementation(network)  # type: ignore
        super().__init__(
            implementation=WitnessNode(
                witnesses=witnesses,
                network=network_implementation,
                handle=self,
            )
        )
