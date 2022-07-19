from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Optional

from test_tools.__private.witness_node import WitnessNode

if TYPE_CHECKING:
    from test_tools.__private.network import Network
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class InitNode(WitnessNode):
    """Node which is ready to produce blocks"""

    def __init__(self, *, name: str = 'InitNode', network: Optional[Network], handle: Optional[NodeHandle] = None):
        super().__init__(name=name, network=network, witnesses=['initminer'], handle=handle)

        self.config.enable_stale_production = True
        self.config.required_participation = 0
