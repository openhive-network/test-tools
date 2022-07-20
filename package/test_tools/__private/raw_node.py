from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Optional

from test_tools.__private.node import Node

if TYPE_CHECKING:
    from test_tools.__private.network import Network
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class RawNode(Node):
    def __init__(
        self, *, name: str = 'RawNode', network: Optional[Network] = None, handle: Optional[NodeHandle] = None
    ):
        super().__init__(name=name, network=network, handle=handle)
