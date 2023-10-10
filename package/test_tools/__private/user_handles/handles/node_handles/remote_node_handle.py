from __future__ import annotations

from typing import TYPE_CHECKING

from test_tools.__private.remote_node import RemoteNode
from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase

if TYPE_CHECKING:
    from helpy._interfaces.url import HttpUrl, WsUrl


class RemoteNodeHandle(NodeHandleBase):
    def __init__(self, http_endpoint: HttpUrl | str, *, ws_endpoint: WsUrl | str | None = None) -> None:
        super().__init__(implementation=RemoteNode(http_endpoint, ws_endpoint=ws_endpoint))
