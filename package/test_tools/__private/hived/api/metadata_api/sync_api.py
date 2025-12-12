from __future__ import annotations

from beekeepy.handle.remote import AbstractSyncApi

from .models import GetMetadata


class MetadataApi(AbstractSyncApi):
    api = AbstractSyncApi.endpoint_jsonrpc

    @api
    def get_metadata(self, *, account: str) -> GetMetadata:
        raise NotImplementedError
