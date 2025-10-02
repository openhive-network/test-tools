from __future__ import annotations

from beekeepy.handle.remote import AbstractSyncApi

from schemas.apis import network_node_api


class NetworkNodeApi(AbstractSyncApi):
    api = AbstractSyncApi.endpoint_jsonrpc

    @api
    def get_info(self) -> network_node_api.GetInfo:
        raise NotImplementedError

    @api
    def add_node(self, *, endpoint: str) -> network_node_api.AddNode:
        raise NotImplementedError

    @api
    def set_allowed_peers(self, *, allowed_peers: list[str]) -> network_node_api.SetAllowedPeers:
        raise NotImplementedError

    @api
    def get_connected_peers(self) -> network_node_api.GetConnectedPeers:
        raise NotImplementedError
