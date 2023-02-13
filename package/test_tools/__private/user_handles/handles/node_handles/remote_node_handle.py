import typing
from typing import Optional

from test_tools.__private.remote_node import RemoteNode
from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handle import Handle


class RemoteNodeHandle(Handle):
    def __init__(self, http_endpoint: str, *, ws_endpoint: Optional[str] = None):
        super().__init__(implementation=RemoteNode(http_endpoint, ws_endpoint=ws_endpoint))

        self.api = self.__implementation.api

    @property
    def __implementation(self) -> RemoteNode:
        return typing.cast(RemoteNode, get_implementation(self))

    def get_last_block_number(self) -> int:
        """Returns number of the newest block known to node."""
        response = self.api.database.get_dynamic_global_properties()
        return response["head_block_number"]
