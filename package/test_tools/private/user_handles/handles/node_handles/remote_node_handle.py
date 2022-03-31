import typing
from typing import Optional

from test_tools.private.remote_node import RemoteNode
from test_tools.private.user_handles.get_implementation import get_implementation
from test_tools.private.user_handles.handle import Handle


class RemoteNodeHandle(Handle):
    def __init__(self, http_endpoint: str, *, ws_endpoint: Optional[str] = None):
        super().__init__(
            implementation=RemoteNode(http_endpoint, ws_endpoint=ws_endpoint)
        )

        self.api = self.__implementation.api

    @property
    def __implementation(self) -> RemoteNode:
        return typing.cast(RemoteNode, get_implementation(self))
