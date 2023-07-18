from typing import Optional

from test_tools.__private.remote_node import RemoteNode
from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase


class RemoteNodeHandle(NodeHandleBase):
    def __init__(self, http_endpoint: str, *, ws_endpoint: Optional[str] = None):
        super().__init__(implementation=RemoteNode(http_endpoint, ws_endpoint=ws_endpoint))
