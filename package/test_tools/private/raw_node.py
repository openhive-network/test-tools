from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from test_tools.private.node import Node

if TYPE_CHECKING:
    from test_tools.private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class RawNode(Node):
    def __init__(self, *, name: str = 'RawNode', handle: Optional[NodeHandle] = None):
        super().__init__(name=name, handle=handle)
