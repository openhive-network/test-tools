from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from test_tools.private.preconfigured_node import PreconfiguredNode

if TYPE_CHECKING:
    from test_tools.private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class ApiNode(PreconfiguredNode):
    def __init__(self, *, name: str = 'ApiNode', handle: Optional[NodeHandle] = None):
        super().__init__(name=name, handle=handle)

        self.config.plugin.remove('witness')
