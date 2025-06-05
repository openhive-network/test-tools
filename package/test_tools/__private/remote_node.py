from __future__ import annotations

from typing import TYPE_CHECKING

from beekeepy.interfaces import HttpUrl, P2PUrl, WsUrl

from test_tools.__private.base_node import BaseNode

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.node_handles.remote_node_handle import RemoteNodeHandle


class RemoteNode(BaseNode):
    def __init__(
        self,
        http_endpoint: HttpUrl | str,
        *,
        ws_endpoint: WsUrl | str | None = None,
        handle: RemoteNodeHandle | None = None,
    ) -> None:
        super().__init__(name="RemoteNode", handle=handle)

        self.http_endpoint = HttpUrl(http_endpoint, protocol="http")
        self.__ws_endpoint: WsUrl | None = WsUrl(ws_endpoint, protocol="ws") if ws_endpoint is not None else None

    def get_version(self) -> dict[str, str]:
        return self.api.database.get_version().dict()

    def get_ws_endpoint(self) -> WsUrl | None:
        if self.__ws_endpoint is None:
            return None

        return self.__ws_endpoint

    def get_http_endpoint(self) -> HttpUrl:
        return self.http_endpoint

    def get_p2p_endpoint(self) -> P2PUrl:
        return P2PUrl(self.api.network_node.get_info().listening_on)

    @staticmethod
    def is_running() -> bool:
        return True
