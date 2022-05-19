from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase
from test_tools.__private.witness_node import WitnessNode

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle as Network


class WitnessNodeHandle(NodeHandleBase):
    def __init__(self, *, witnesses: Optional[List[str]] = None, network: Optional[Network] = None):
        super().__init__(
            implementation=WitnessNode(
                witnesses=witnesses,
                network=get_implementation(network),
                handle=self,
            )
        )
