from __future__ import annotations

from beekeepy.handle.remote import AbstractSyncApi

from .models import FindAccountMetadata, GetAccountMetadata


class MetadataApi(AbstractSyncApi):
    api = AbstractSyncApi.endpoint_jsonrpc

    @api
    def get_account_metadata(self, *, account: str) -> GetAccountMetadata:
        raise NotImplementedError

    @api
    def find_account_metadata(self, *, accounts: list[str]) -> FindAccountMetadata:
        raise NotImplementedError
