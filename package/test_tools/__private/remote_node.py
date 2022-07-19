from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Optional

from test_tools.__private import communication
from test_tools.__private.node_message import NodeMessage
from test_tools.__private.scope import context
from test_tools.__private.url import Url
from test_tools.__private.user_handles.implementation import Implementation as UserHandleImplementation
from test_tools.node_api.node_apis import Apis

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.node_handles.remote_node_handle import RemoteNodeHandle


class RemoteNode(UserHandleImplementation):
    def __init__(self, http_endpoint: str, *, ws_endpoint: Optional[str] = None,
                 handle: Optional[RemoteNodeHandle] = None):
        super().__init__(handle=handle)

        self.api = Apis(self)
        self.name = context.names.register_numbered_name('RemoteNode')
        self.__http_endpoint: Url = Url(http_endpoint, protocol='http')
        self.__ws_endpoint: Optional[Url] = Url(ws_endpoint, protocol='ws') if ws_endpoint is not None else None

    def __str__(self) -> str:
        return self.name

    def send(self, method, params=None, jsonrpc='2.0', id_=1, *, only_result: bool = True):
        response = communication.request(
            self.__http_endpoint.as_string(),
            NodeMessage(method, params, jsonrpc, id_).as_json()
        )

        return response['result'] if only_result else response

    def get_ws_endpoint(self):
        if self.__ws_endpoint is None:
            return None

        return self.__ws_endpoint.as_string(with_protocol=False)

    @staticmethod
    def is_running():
        return True
