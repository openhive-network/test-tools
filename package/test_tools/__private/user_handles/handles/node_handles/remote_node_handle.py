import typing
from typing import Optional

from test_tools.__private.remote_node import RemoteNode
from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handle import Handle


class RemoteNodeHandle(Handle[RemoteNode]):
    def __init__(self, http_endpoint: str, *, ws_endpoint: Optional[str] = None):
        super().__init__(implementation=RemoteNode(http_endpoint, ws_endpoint=ws_endpoint))

        self.api = self._implementation.api
